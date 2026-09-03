from django.urls import include, path
from rest_framework.routers import DefaultRouter

from products.api_views import CategoryTreeView, ProductListView, ProductDetailView
from accounts.api_views import csrf_view, api_login, api_logout, me_view


router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', CategoryTreeView.as_view(), name='api-categories'),
    path('products/', ProductListView.as_view(), name='api-products'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='api-product-detail'),
    path('csrf/', csrf_view, name='api-csrf'),
    path('auth/login/', api_login, name='api-login'),
    path('auth/logout/', api_logout, name='api-logout'),
    path('me/', me_view, name='api-me'),
]