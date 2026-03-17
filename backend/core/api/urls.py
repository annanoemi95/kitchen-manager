from django.urls import path, include

urlpatterns = [
    path("orders/", include("core.api.orders.urls")),
]