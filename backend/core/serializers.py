from rest_framework import serializers
from .models import User, Category, Dish, Order, OrderItem, Review

# Serializer per l'utente: proteggiamo i dati sensibili
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'role'
        ]

# Serializer per le categorie
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name'
        ]

# Serializer per i piatti con riferimento al nome della categoria
class DishSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Dish
        fields = [
            'id',
            'name',
            'description',
            'price',
            'category',
            'category_name',
            'is_active',
            'is_available'
        ]

# Serializer per i singoli elementi degli ordini (Nested)
class OrderItemSerializer(serializers.ModelSerializer):
    dish_details = DishSerializer(source='dish', read_only=True)

    class Meta:
        model = OrderItem
        # Inserito unit_price come richiesto
        fields = [
            'id',
            'dish',
            'dish_details',
            'quantity',
            'unit_price'
        ]
        read_only_fields = ['unit_price']  # Viene impostato dal sistema al momento dell'ordine

# Serializer principale per gli Ordini
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        # Inserito total_amount come richiesto
        fields = [
            'id',
            'user',
            'status',
            'items',
            'created_at',
            'notes',
            'total_amount'
        ]
        read_only_fields = ['total_amount']

# Serializer per le recensioni
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        # Il rating ora seguirà la validazione 1-5 definita nel modello
        fields = [
            'id',
            'order',
            'rating',
            'comment',
            'created_at'
        ]