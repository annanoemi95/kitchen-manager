from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from core.views import (
    CategoryListView,
    DishListView,
    OrderListCreateView,
    ReviewViewSet,
    RegisterView,
    CustomTokenObtainPairView,
    MeView,
)

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    # ── AUTH ──────────────────────────────
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('auth/me/', MeView.as_view(), name='auth-me'),

    # ── MENU ──────────────────────────────
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('dishes/', DishListView.as_view(), name='dish-list'),

    # ── ORDERS ────────────────────────────
    path("orders/", include("core.api.orders.urls")),
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),

    # ── REVIEWS + AI ──────────────────────
    path('', include(router.urls)),
]