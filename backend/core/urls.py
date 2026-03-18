from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CategoryListView,
    DishListView,
    OrderListCreateView,
    ReviewCreateView,
    RegisterView,
    CustomTokenObtainPairView,
    MeView,
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('dishes/', DishListView.as_view(), name='dish-list'),
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('reviews/', ReviewCreateView.as_view(), name='review-create'),

    # ── AUTH ──────────────────────────────
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
]