from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Category, Dish, Order, Review
from .serializers import (
    CategorySerializer,
    DishSerializer,
    OrderSerializer,
    ReviewSerializer,
    RegisterSerializer,
    UserMeSerializer,
    CustomTokenObtainPairSerializer
)

class RegisterView(APIView):
    """
    POST /auth/register/
    Registrazione pubblica — crea sempre un customer.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserMeSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    POST /auth/login/
    Login customer e admin — restituisce access, refresh, role, user_id.
    """
    serializer_class = CustomTokenObtainPairSerializer


class MeView(APIView):
    """
    GET /auth/me/
    Restituisce i dati dell'utente autenticato. Richiede token valido.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserMeSerializer(request.user).data)


# --- VIEWS PER IL MENU (Pubbliche) ---

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class DishListView(generics.ListAPIView):
    queryset = Dish.objects.filter(is_active=True)
    serializer_class = DishSerializer
    permission_classes = [permissions.AllowAny]


# --- VIEWS PER GLI ORDINI (Protette) ---

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Un cliente vede solo i PROPRI ordini, un admin vede TUTTO
        user = self.request.user
        if user.role == 'admin':
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        # Assegna automaticamente l'utente loggato all'ordine
        serializer.save(user=self.request.user)


# --- VIEWS PER LE RECENSIONI ---

class ReviewCreateView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order = serializer.validated_data["order"]
        if order.user != self.request.user:
            raise PermissionDenied("Non puoi recensire un ordine non tuo.")
        serializer.save()

