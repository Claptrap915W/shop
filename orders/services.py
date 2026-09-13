import uuid                          
from decimal import Decimal          
from django.db import transaction    
from django.utils import timezone   
from products.models import ProductVariant  
from users.models import UserProfile 
from .models import Order, OrderItem, Payment  
from carts.models import Cart as DBCart

DECLINED_CARD_LAST_FOUR = '0002' 

class InsufficientStockError(Exception):
    def __init__(self, message, items=None):
        super().__init__(message)  
        self.items = items or []

class PaymentDeclinedError(Exception):
    def __init__(self, message):
        super().__init__(message)


def generate_order_no():
    return f"ORD-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4().int)[-12:]}"


@transaction.atomic  
def place_order(user, cart, shipping_data, payment_data):
    cart_items = list(cart)
    if not cart_items:
        raise ValueError('Cart is empty')

    variant_ids = [item['variant'].id for item in cart_items]

    variants = {
        v.id: v
        for v in ProductVariant.objects.select_related('product', 'color')  
            .select_for_update()  # 這些列「上鎖」，其他表會自動鎖要修改必須等 commit
            .filter(id__in=variant_ids)
    }

    insufficient = []  # 收集所有缺貨的項目
    for item in cart_items:
        variant = variants.get(item['variant'].id)
        if not variant or variant.stock < item['quantity']:
            insufficient.append({
                'product': item['variant'].product.name,    
                'requested': item['quantity'],             
                'available': variant.stock if variant else 0,  
            })

    if insufficient:
        raise InsufficientStockError('Insufficient stock', insufficient)

    order_subtotal = Decimal('0.00')
    order = Order.objects.create(
        user=user,
        order_no=generate_order_no(),
        # 下面四個是「收件快照」：從 shipping_data 複製一份進來
        # 未來使用者改 profile 不會影響這張訂單的收件資料
        full_name=shipping_data['full_name'],
        email=shipping_data['email'],
        phone=shipping_data['phone'],
        address=shipping_data['address'],
        total=Decimal('0.00'),
        subtotal=Decimal('0.00'),   
        shipping_fee=Decimal('0.00'),
        tax=Decimal('0.00'),
        discount_amount=Decimal('0.00'),
        status='pending',         
    )

    for item in cart_items:
        variant = variants[item['variant'].id]   
        price = Decimal(str(item['price']))       
        qty = item['quantity']                    
        line_subtotal = price * qty                    
        order_subtotal += line_subtotal                        

        # 只存 media 路徑字串（如 'products/tshirt_red.jpg'），不複製實體檔案
        # 若商品未來換圖，歷史訂單仍會顯示結帳當時的圖片路徑
        image_path = ''
        image_alt = ''
        if item.get('image'):
            image_path = item['image'].name           # .name 取得相對路徑
            image_alt = item.get('image_text', '')    

        # 從 variant 當下的值複製一份過來，未來商品改名不影響歷史訂單顯示
        OrderItem.objects.create(
            order=order,                          
            variant=variant,                      
            product_name=variant.product.name,    
            product_slug=variant.product.slug,    
            sku=variant.sku,                      
            color_name=variant.color.name,        
            size=variant.size,                    
            image_path=image_path,                
            image_alt=image_alt,                  
            price=price,                          
            quantity=qty,                         
            subtotal=line_subtotal,                    
        )

        # ---- 扣減庫存 ----
        variant.stock -= qty
        # update_fields=['stock']：只更新 stock 欄位
        variant.save(update_fields=['stock'])

    profile, _ = UserProfile.objects.get_or_create(user=user)

    shipping_fee = Decimal('0.00')
    tax = Decimal('0.00')
    discount_amount = Decimal('0.00')
    subtotal = order_subtotal
    order_total = subtotal + shipping_fee + tax - discount_amount
    
    earned_points = int(order_subtotal)
    profile.points += earned_points
    profile.save(update_fields=['points'])
    order.subtotal = subtotal
    order.tax = tax
    order.discount_amount = discount_amount
    order.shipping_fee = shipping_fee
    order.total = order_total       
    order.status = 'paid'        
    order.save(update_fields=[
        'subtotal', 'shipping_fee', 'tax', 'discount_amount','status', 'total']) 

    if payment_data.get('card_last_four') == DECLINED_CARD_LAST_FOUR:
        raise PaymentDeclinedError('Card declined by issuer.')

    Payment.objects.create(
        order=order,                                              
        method=payment_data.get('method', 'credit_card'),         
        status='success',                                         
        amount=order_total,                                             
        card_last_four=payment_data.get('card_last_four', ''),    
        transaction_id=f"TXN-{uuid.uuid4().hex[:10].upper()}",    
        paid_at=timezone.now(),                                   
    )

    db_cart = DBCart.objects.filter(user=user).first()
    if db_cart is not None:
        db_cart.items.all().delete()

    return order                 