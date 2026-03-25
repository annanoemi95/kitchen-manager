from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Category, Dish, Order, Review
from .serializers import (
    CategorySerializer,
    DishSerializer,
    OrderSerializer,
    ReviewSerializer,
    RegisterSerializer,
    UserMeSerializer,
    CustomTokenObtainPairSerializer,
)
from .permissions import IsAdmin
from .services import AIService


# ──────────────────────────────────────────
# AUTH VIEWS (Anna)
# ──────────────────────────────────────────

class RegisterView(APIView):
    """
    POST /api/auth/register/
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
    POST /api/auth/login/
    Login customer e admin — restituisce access, refresh, role, user_id.
    """
    serializer_class = CustomTokenObtainPairSerializer


class MeView(APIView):
    """
    GET /api/auth/me/
    Restituisce i dati dell'utente autenticato. Richiede token valido.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserMeSerializer(request.user).data)


# ──────────────────────────────────────────
# MENU VIEWS (Marika)
# ──────────────────────────────────────────

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class DishListView(generics.ListAPIView):
    queryset = Dish.objects.filter(is_active=True)
    serializer_class = DishSerializer
    permission_classes = [permissions.AllowAny]


class AdminDishListCreateView(generics.ListCreateAPIView):
    serializer_class = DishSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return Dish.objects.select_related('category').order_by('category__name', 'name')


class AdminDishDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DishSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return Dish.objects.select_related('category').all()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.is_available = False
        instance.save(update_fields=['is_active', 'is_available'])


# ──────────────────────────────────────────
# ORDER VIEWS (Chiara)
# ──────────────────────────────────────────

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if (
            getattr(user, "role", None) == "admin"
            or user.is_staff
            or user.is_superuser
        ):
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ──────────────────────────────────────────
# REVIEW VIEWS (Isabelle)
# ──────────────────────────────────────────

class ReviewViewSet(viewsets.ModelViewSet):
    """
    Gestisce il ciclo di vita delle recensioni e l'analisi AI per l'admin.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if (
            getattr(user, "role", None) == "admin"
            or user.is_staff
            or user.is_superuser
        ):
            return Review.objects.all()
        return Review.objects.filter(order__user=user)

    def perform_create(self, serializer):
        order = serializer.validated_data["order"]

        if order.user != self.request.user:
            raise PermissionDenied("Non puoi recensire un ordine non tuo.")

        if order.status != "delivered":
            raise PermissionDenied(
                "Puoi recensire l'ordine solo dopo la consegna (stato: delivered)."
            )

        serializer.save()

    @action(detail=False, methods=["get"], url_path="ai-summary")
    def ai_summary(self, request):
        if not (
            getattr(request.user, "role", None) == "admin"
            or request.user.is_staff
            or request.user.is_superuser
        ):
            return Response(
                {"detail": "Accesso negato. Funzionalità riservata all'amministratore."},
                status=status.HTTP_403_FORBIDDEN,
            )

        reviews = Review.objects.all()
        if reviews.count() < 3:
            return Response(
                {"detail": "Dati insufficienti: servono almeno 3 recensioni per avviare l'IA."},
                status=status.HTTP_200_OK,
            )

        analysis = AIService.analyze_reviews(reviews)

        return Response(
            {
                "status": "Analisi Reale Completata",
                "provider": "Gemini 2.5 Flash",
                "results": analysis,
            },
            status=status.HTTP_200_OK,
        )
