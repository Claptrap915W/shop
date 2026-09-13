from django.conf import settings
from django.db import models


class Order(models.Model):
    """訂單主檔；收件欄為 checkout 快照，付款見 Payment。"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    FULFILLMENT_STATUS_CHOICES = [
        ('unfulfilled', 'Unfulfilled'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
    )
    order_no = models.CharField(max_length=50, unique=True)

    # checkout 快照，不隨 profile 變動
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()

    total = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    fulfillment_status = models.CharField(
        max_length=20,
        choices=FULFILLMENT_STATUS_CHOICES,
        default='unfulfilled',
    )

    internal_notes = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.order_no


class OrderItem(models.Model):
    """訂單明細；顯示用快照欄，不依 live Product/Variant。"""

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name='items',
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.PROTECT,
        related_name='order_items',
    )

    # 下單當下快照（services 寫入）
    product_name = models.CharField(max_length=200)
    product_slug = models.SlugField(max_length=200, blank=True)
    sku = models.CharField(max_length=50, blank=True)
    color_name = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=5)
    image_path = models.CharField(max_length=255, blank=True)  # media 相對路徑，非複製檔案
    image_alt = models.CharField(max_length=150, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    @property
    def image_url(self):
        if self.image_path:
            return f'{settings.MEDIA_URL}{self.image_path}'
        return ''

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'


class Payment(models.Model):
    """一對一付款紀錄；僅存末四碼，不存完整卡號/CVC。"""

    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment',
    )
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='credit_card')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    card_last_four = models.CharField(max_length=4, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.order.order_no} - {self.get_status_display()}'
