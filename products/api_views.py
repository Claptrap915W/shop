from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Category, Product
from products.serializers import CategoryTreeSerializer, ProductDetailSerializer, ProductListSerializer

class CategoryTreeView(APIView):
    def get(self, request):
        categories = list(
            Category.objects.filter(is_active=True)
            .annotate(
                direct_count=Count(
                    'products',
                    filter=Q(products__is_active=True),
                )
            )
            .order_by('name')
        )

        by_id = {c.id: c for c in categories}

        for cat in categories:
            cat.child_list = []
            cat.sub_product_count = cat.direct_count

        for cat in categories:
            if cat.parent_id is not None and cat.parent_id in by_id:
                by_id[cat.parent_id].child_list.append(cat)

        roots = [cat for cat in categories if cat.parent_id is None]
        for root in roots:
            root.total_product_count = root.direct_count + sum(
                child.direct_count for child in root.child_list
            )
        
        return Response(CategoryTreeSerializer(roots, many=True).data)

class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        products = Product.active.select_related('category').all()

        query = self.request.query_params.get('q', '').strip()
        if query:
            products = products.filter(
                Q(name__icontains=query) |
                Q(variants__sku__icontains=query) |
                Q(category__name__icontains=query) |
                Q(variants__color__name__icontains=query) |
                Q(variants__size__icontains=query)
            ).distinct()

        category_slug = self.request.query_params.get('category', '')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            category_ids = [category.id] + list(
                category.children.values_list('id', flat=True)
            )
            products = products.filter(category_id__in=category_ids)

        min_p = self.request.query_params.get('min', '')
        if min_p:
            try:
                products = products.filter(base_price__gte=float(min_p))
            except ValueError:
                pass

        max_p = self.request.query_params.get('max', '')
        if max_p:
            try:
                products = products.filter(base_price__lte=float(max_p))
            except ValueError:
                pass

        return products

class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
    queryset = Product.active.prefetch_related(
        'variants__color',
        'images__color',
    ).select_related('category')