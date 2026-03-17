from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from core.models import Dish, Order, OrderItem


ORDER_ITEM_FIELD_NAMES = {field.name for field in OrderItem._meta.fields}
ORDER_FIELD_NAMES = {field.name for field in Order._meta.fields}


class OrderItemInputSerializer(serializers.Serializer):
    dish_id = serializers.PrimaryKeyRelatedField(
        queryset=Dish.objects.all(),
        source="dish",
    )
    quantity = serializers.IntegerField(min_value=1)


class OrderItemOutputSerializer(serializers.ModelSerializer):
    dish_id = serializers.IntegerField(source="dish.id", read_only=True)
    dish_name = serializers.CharField(source="dish.name", read_only=True)
    category = serializers.CharField(source="dish.category.name", read_only=True)
    unit_price = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "dish_id",
            "dish_name",
            "category",
            "quantity",
            "unit_price",
            "line_total",
        ]

    def get_unit_price(self, obj):
        if "unit_price" in ORDER_ITEM_FIELD_NAMES and getattr(obj, "unit_price", None) is not None:
            return obj.unit_price
        return obj.dish.price

    def get_line_total(self, obj):
        unit_price = self.get_unit_price(obj)
        return unit_price * obj.quantity


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemOutputSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "username",
            "status",
            "created_at",
            "notes",
            "items",
            "total_amount",
        ]

    def get_total_amount(self, obj):
        if "total_amount" in ORDER_FIELD_NAMES and getattr(obj, "total_amount", None) is not None:
            return obj.total_amount

        total = Decimal("0.00")
        for item in obj.items.all():
            if "unit_price" in ORDER_ITEM_FIELD_NAMES and getattr(item, "unit_price", None) is not None:
                total += item.unit_price * item.quantity
            else:
                total += item.dish.price * item.quantity
        return total


class OrderCreateSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    items = OrderItemInputSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("An order must contain at least one item.")

        seen_dish_ids = set()

        for item in value:
            dish = item["dish"]

            if dish.id in seen_dish_ids:
                raise serializers.ValidationError(
                    f"Dish '{dish.name}' was sent more than once. Use a single row and increase quantity."
                )
            seen_dish_ids.add(dish.id)

            if not dish.is_active:
                raise serializers.ValidationError(
                    f"Dish '{dish.name}' is not active and cannot be ordered."
                )
            if not dish.is_available:
                raise serializers.ValidationError(
                    f"Dish '{dish.name}' is currently unavailable."
                )

        return value

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        items_data = validated_data.pop("items")
        notes = validated_data.get("notes")

        order_kwargs = {
            "user": request.user,
            "status": "received",
        }
        if "notes" in ORDER_FIELD_NAMES:
            order_kwargs["notes"] = notes

        order = Order.objects.create(**order_kwargs)

        total = Decimal("0.00")

        for item_data in items_data:
            dish = item_data["dish"]
            quantity = item_data["quantity"]
            unit_price = dish.price

            order_item_kwargs = {
                "order": order,
                "dish": dish,
                "quantity": quantity,
            }
            if "unit_price" in ORDER_ITEM_FIELD_NAMES:
                order_item_kwargs["unit_price"] = unit_price

            OrderItem.objects.create(**order_item_kwargs)
            total += unit_price * quantity

        if "total_amount" in ORDER_FIELD_NAMES:
            order.total_amount = total
            order.save(update_fields=["total_amount"])

        return order


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["status"]

    def validate_status(self, value):
        current_status = self.instance.status
        allowed_flow = ["received", "preparing", "ready", "delivered"]

        current_index = allowed_flow.index(current_status)

        if current_index == len(allowed_flow) - 1:
            raise serializers.ValidationError("Delivered orders cannot change status anymore.")

        expected_next_status = allowed_flow[current_index + 1]
        if value != expected_next_status:
            raise serializers.ValidationError(
                f"Invalid transition. Next allowed status is '{expected_next_status}'."
            )

        return value

