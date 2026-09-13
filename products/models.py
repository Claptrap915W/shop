from django.db import models
from django.urls import reverse
from django.db import IntegrityError, transaction
from django.utils.text import slugify


class Category(models.Model):
    """分類樹；parent 指向父分類。"""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    is_active = models.BooleanField(default=True, verbose_name='Is_Published')
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='children',
    )

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ActiveProductManager(models.Manager):
    """上架商品；prefetch images / variants 減 N+1。"""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True).prefetch_related('images', 'variants')


class Product(models.Model):
    """商品主檔；結帳價格以 Variant 為準，base_price 供列表／篩選。"""

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='category',
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField(null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d/', null=True, blank=True)

    objects = models.Manager()
    active = ActiveProductManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['created_at'])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:product', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Color Name (e.g. Classic Black)')
    slug = models.SlugField(unique=True, max_length=50)
    hex_code = models.CharField(max_length=7, verbose_name='HexCode (e.g.#000000)', help_text='Format: #RRGGBB')

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """商品多圖；可綁定顏色，display_order 決定排序。"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    alt_text = models.CharField(max_length=150, blank=True, verbose_name='SeoKeywords')
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['display_order']
        indexes = [models.Index(fields=['display_order'])]

    def save(self, *args, **kwargs):
        if not self.alt_text and self.product:
            self.alt_text = f"{self.product.name}-{self.color}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductVariant(models.Model):
    """可售 SKU：product + color + size；庫存與價格在此。"""

    SIZE_CHOICES = [
        ('XS', 'XS'), ('S', 'S'), ('M', 'M'),
        ('L', 'L'), ('XL', 'XL'), ('2XL', '2XL'), ('3XL', '3XL'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name='variants')
    size = models.CharField(max_length=5, choices=SIZE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0, db_index=True)
    sku = models.CharField(max_length=50, unique=True, blank=True)

    class Meta:
        unique_together = ('product', 'color', 'size')

    
    def save(self, *args, **kwargs):
        if self.price is None or self.price == 0:
            self.price = self.product.base_price
        
        if not self.sku:
            product_slug = self.product.slug[:20]
            color_name = self.color.name[:2].upper()
            base_sku = f"{product_slug}-{color_name}-{self.size}"

            self.sku = base_sku
            counter = 0
            while True:
                try: 
                    with transaction.atomic():
                        super().save(*args, **kwargs)
                    return 
                except IntegrityError:
                    counter += 1
                    self.sku = f"{base_sku}-{counter}"
        else:
            super().save(*args, **kwargs)

    @property
    def final_price(self):
        if self.price is not None:
            return self.price
        return self.product.base_price

    def __str__(self):
        return f"{self.product.name} - {self.color.name} / {self.size}"
