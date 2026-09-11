import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView

from carts.cart import Cart
from . import services
from .serializers import CheckoutWriteSerializer, OrderListSerializer, OrderDetailSerializer
from .models import Order

logger = logging.getLogger(__name__)

class OrderListCreateView(ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def post(self, request):
        serializer = CheckoutWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart(request)
        if len(cart) == 0:
            return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = services.place_order(
                request.user,
                cart,
                serializer.get_shipping_data(),
                serializer.get_payment_data(),
            )
        except services.InsufficientStockError as e:
            return Response(
                {'reason': 'stock', 'items': e.items},
                status=status.HTTP_409_CONFLICT,
            )
        except ValueError:
            return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart.clear()
        except Exception:
            logger.exception('Failed to clear cart after order %s was created', order.order_no)
        return Response({'order_no': order.order_no}, status=status.HTTP_201_CREATED)

class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "order_no"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('payment').prefetch_related('items')




