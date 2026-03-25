from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Order
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)


class IsProjectAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        return (
            getattr(user, "role", None) == "admin"
            or user.is_staff
            or user.is_superuser
        )


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = (
            Order.objects.select_related("user")
            .prefetch_related("items__dish__category")
            .order_by("-created_at")
        )

        is_admin = (
            getattr(request.user, "role", None) == "admin"
            or request.user.is_staff
            or request.user.is_superuser
        )

        if not is_admin:
            queryset = queryset.filter(user=request.user)
        else:
            # ── FILTRI ADMIN ─────────────────────────────
            status_param = request.query_params.get('status')
            if status_param:
                queryset = queryset.filter(status=status_param)

            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            if date_from:
                queryset = queryset.filter(created_at__date__gte=date_from)
            if date_to:
                queryset = queryset.filter(created_at__date__lte=date_to)

            customer = request.query_params.get('customer')
            if customer:
                queryset = queryset.filter(user__username__icontains=customer)

    
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        order = (
            Order.objects.select_related("user")
            .prefetch_related("items__dish__category")
            .get(pk=order.pk)
        )

        output_serializer = OrderSerializer(order)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        queryset = (
            Order.objects.select_related("user")
            .prefetch_related("items__dish__category")
        )
        order = get_object_or_404(queryset, pk=pk)

        is_admin = (
            getattr(request.user, "role", None) == "admin"
            or request.user.is_staff
            or request.user.is_superuser
        )

        if not is_admin and order.user_id != request.user.id:
            return Response(
                {"detail": "You do not have permission to view this order."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data)


class OrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsProjectAdmin]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        order = (
            Order.objects.select_related("user")
            .prefetch_related("items__dish__category")
            .get(pk=order.pk)
        )
        output_serializer = OrderSerializer(order)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
