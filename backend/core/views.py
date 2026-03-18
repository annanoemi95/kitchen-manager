from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Category, Dish, Order, Review
from .serializers import (
    CategorySerializer,
    DishSerializer,
    OrderSerializer,
    ReviewSerializer,
)
from .services import AIService


User = get_user_model()


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Registrazione pubblica: crea sempre un customer.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username", "").strip()
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")
        password_confirm = request.data.get("password_confirm", "")

        if not username:
            return Response(
                {"username": ["Questo campo è obbligatorio."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not password:
            return Response(
                {"password": ["Questo campo è obbligatorio."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if password != password_confirm:
            return Response(
                {"password": ["Le password non coincidono."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"username": ["Questo username è già in uso."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(password)
        except DjangoValidationError as exc:
            return Response(
                {"password": list(exc.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="customer",
        )

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomTokenObtainPairView(APIView):
    """
    POST /api/auth/login/
    Login customer e admin: restituisce access, refresh, role e user_id.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username", "")
        password = request.data.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Credenziali non valide."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        refresh["role"] = user.role

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "role": user.role,
                "user_id": user.id,
            },
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    """
    GET /api/auth/me/
    Restituisce i dati dell'utente autenticato.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            }
        )


# --- BLOCCO MENU (Marika) ---
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class DishListView(generics.ListAPIView):
    queryset = Dish.objects.filter(is_active=True)
    serializer_class = DishSerializer
    permission_classes = [permissions.AllowAny]


# --- BLOCCO ORDINI (Chiara) ---
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


# --- BLOCCO RECENSIONI & AI (Isabelle) ---
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
