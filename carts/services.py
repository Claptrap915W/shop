from .models import Cart, CartItem
from products.models import ProductVariant
from loguru import logger

def merge_session_cart_into_db(request, user):
    cart, created= Cart.objects.get_or_create(user=user)
    session_cart = request.session.get('carts', {})

    for item in session_cart:
        try:
            variant = ProductVariant.objects.get(pk = item)
            quantity = session_cart[item]['quantity']
            CartItem.objects.update_or_create(cart=cart, variant=variant, defaults={'quantity': quantity})
        except ProductVariant.DoesNotExist:
            logger.warning(f"variant id {item} not found while merging cart, skipped")
