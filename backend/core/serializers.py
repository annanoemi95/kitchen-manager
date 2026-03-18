from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Category, Dish, Order, OrderItem, Review

# ──────────────────────────────────────────
# AUTH SERIALIZERS (Anna)
# ──────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm']
        extra_kwargs = {
            'email': {'required': False}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({"password": "Le password non coincidono."})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role='customer',  # nessun utente si auto-assegna admin
        )


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']
        read_only_fields = ['id', 'username', 'email', 'role']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role  # ruolo nel payload JWT
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role    # ruolo nel body della response
        data['user_id'] = self.user.id
        return data



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