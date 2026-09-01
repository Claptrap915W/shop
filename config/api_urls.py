from django.urls import include, path
from rest_framework.routers import DefaultRouter

from products.api_views import CategoryTreeView, ProductListView, ProductDetailView


router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', CategoryTreeView.as_view(), name='api-categories'),
    path('products/', ProductListView.as_view(), name='api-products'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='api-product-detail'),
]