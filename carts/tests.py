from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from products.models import Category, Product, Color, ProductVariant

def _make_variant(stock=1):
    category = Category.objects.create(name="Test Cat", slug="test-cat")
    color = Color.objects.create(name="Black", slug='black', hex_code="#000000")
    fake_image = SimpleUploadedFile("t.jpg", b"x", content_type="image/jpeg")
    product = Product.objects.create(
        category=category,
        name="Test Product",
        slug="test-product",
        base_price="29.90",
        is_active=True,
        image=fake_image,
    )
    return ProductVariant.objects.create(
        product=product,
        color=color,
        size="M",
        stock=stock,
    )

class CartItemCreateTests(TestCase):
    def setUp(self):
        self.variant = _make_variant(stock=1)

    def test_missing_variant_id_return_400(self):
        resp = self.client.post(
            reverse("api-cart-items"),
            data={"quantity": 1},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("variant_id", resp.json())

    def test_over_stock_returns_409(self):
        resp = self.client.post(
            reverse("api-cart-items"),
            data={"variant_id": self.variant.id, "quantity": 2},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 409)
        body = resp.json()
        self.assertEqual(body.get("detail"), "Insufficient stock")
        self.assertEqual(body.get("available"), 1)