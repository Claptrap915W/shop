from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from products.models import ProductVariant
from .cart import Cart
from .serializers import CartItemWriteSerializer, CartItemPatchSerializer

class CartListCreateView(APIView):
    def get(self, request):
        cart = Cart(request)
        items = []
        total_price = Decimal('0')

        for item in cart:
            variant = item['variant']
            color = variant.color
            image = item.get('image')

            items.append({
                'variant_id': variant.id,
                'product_name': variant.product.name,
                'sku': variant.sku,
                'size': variant.size,
                'color': (
                    {'id': color.id, 'name': color.name, 'slug': color.slug}
                    if color else None
                ),
                'quantity': item['quantity'],
                'price': str(item['price']),
                'subtotal': str(item['total_price']),
                'image': request.build_absolute_uri(image.url) if image else None,
            })
            total_price += item['total_price']
        
        return Response({
            'items': items,
            'total_quantity' : len(cart),
            'total_price': str(total_price),
        })

    def post(self, request):
        serializer = CartItemWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        variant_id = serializer.validated_data['variant_id']
        quantity = serializer.validated_data['quantity']

        variant = get_object_or_404(ProductVariant, id=variant_id)
        cart = Cart(request)

        current_qty = cart.carts.get(str(variant_id), {}).get('quantity', 0)
        new_qty = current_qty + quantity

        if new_qty > variant.stock:
            return Response(
                {
                    'detail': 'Insufficient stock',
                    'available': variant.stock,
                    'requested': new_qty,
                },
                status=status.HTTP_409_CONFLICT,
            )
        cart.add(variant=variant, quantity=quantity)

        return Response(
            {
                'variant_id': variant.id,
                'quantity': cart.carts[str(variant.id)]['quantity']
            },
            status=status.HTTP_201_CREATED,
        )

class CartItemDetailView(APIView):

    def patch(self, request, variant_id):
        serializer = CartItemPatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        quantity = serializer.validated_data['quantity']
        variant = get_object_or_404(ProductVariant, id=variant_id)
        cart = Cart(request)

        if str(variant_id) not in cart.carts:
            return Response(
                {'detail': 'Item not in cart'},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        if quantity > variant.stock:
            return Response(
                {
                    'detail': 'Insufficient stock',
                    'available': variant.stock,
                    'requested': quantity,
                },
                status=status.HTTP_409_CONFLICT
            )

        cart.add(variant=variant, quantity=quantity, override_quantity=True)

        return Response(
            {'variant_id': variant.id, 'quantity': quantity},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, variant_id):
        variant = get_object_or_404(ProductVariant, id=variant_id)
        cart = Cart(request)

        if str(variant_id) not in cart.carts:
            return Response(
                {'detail': 'Item not in cart'},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        cart.remove(variant)

        return Response(status=status.HTTP_204_NO_CONTENT)