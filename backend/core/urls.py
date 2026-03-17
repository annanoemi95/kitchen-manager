from django.urls import path
from .views import (
    CategoryListView,
    DishListView,
    OrderListCreateView,
    ReviewCreateView
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('dishes/', DishListView.as_view(), name='dish-list'),
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('reviews/', ReviewCreateView.as_view(), name='review-create'),
]