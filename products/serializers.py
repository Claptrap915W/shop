from rest_framework import serializers
from .models import Category, Color, Product, ProductImage, ProductVariant

class CategoryChildSerializer(serializers.ModelSerializer):
    sub_product_count = serializers.IntegerField(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'parent', 'sub_product_count')

class CategoryTreeSerializer(serializers.ModelSerializer):
    children = CategoryChildSerializer(source="child_list", many=True, read_only=True)
    total_product_count = serializers.IntegerField(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'slug',
            'parent',
            'total_product_count',
            'children',
        )

class CategoryBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')

class ProductListSerializer(serializers.ModelSerializer):
    category = CategoryBriefSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'base_price', 'image', 'category')

class ColorBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ('id', 'name', 'slug')

class ProductImageSerializer(serializers.ModelSerializer):
    color = ColorBriefSerializer(read_only=True)

    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'display_order', 'color')

class ProductVariantSerializer(serializers.ModelSerializer):
    color = ColorBriefSerializer(read_only=True)
    price = serializers.DecimalField(
        source='final_price',
        max_digits=10, 
        decimal_places=2, 
        read_only=True
        )
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = ('id', 'sku', 'color', 'size', 'price', 'stock', 'in_stock')

    def get_in_stock(self, obj):
        return obj.stock > 0

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategoryBriefSerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    current_variant = serializers.SerializerMethodField()
    current_color_variants = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'description', 'base_price', 'image', 'category', 'variants', 'images', 'current_variant', 'current_color_variants',)

    def _get_current_color(self, product):
        all_variants = list(product.variants.all())
        if not all_variants:
            return None

        available_colors = list({v.color.id: v.color for v in all_variants}.values())

        request = self.context.get('request')
        current_color_slug = request.query_params.get('color') if request else None

        return next(
            (c for c in available_colors if c.slug == current_color_slug),
            available_colors[0] if available_colors else None,
        )

    def get_current_variant(self, product):
        variants = self.get_current_color_variants(product)
        return variants[0] if variants else None
    
    def get_current_color_variants(self, product):
        cache = getattr(self, '_variants_cache', {})
        if product.pk in cache:
            return cache[product.pk]

        current_color = self._get_current_color(product)
        if not current_color:
            result = []
        else:
            variants = [v for v in product.variants.all() if v.color_id == current_color.id]
            result = ProductVariantSerializer(variants, many=True, context=self.context).data

        cache[product.pk] = result
        self._variants_cache = cache
        return result
