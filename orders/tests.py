from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Color, Product, ProductVariant

User = get_user_model()

CHECKOUT_DATA = {
    "full_name": "Test User",
    "email": "a@example.com",
    "phone": "0912345678",
    "address": "Taipei",
    "card_number": "4111111111111111",
    "card_expiry": "12/28",
    "card_cvc": "123",
}


def _make_variant(stock=2):
    category = Category.objects.create(name="Test Cat", slug="test-cat")
    color = Color.objects.create(name="Black", slug="black", hex_code="#000000")
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


class OrderCheckoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("buyer", password="pw")
        self.client.force_login(self.user)
        self.variant = _make_variant(stock=2)

    def _add_to_cart(self):
        resp = self.client.post(
            reverse("api-cart-items"),
            data={"variant_id": self.variant.id, "quantity": 1},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)

    def test_checkout_returns_201_with_order_no(self):
        self._add_to_cart()
        resp = self.client.post(
            reverse("api-orders"),
            data=CHECKOUT_DATA,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertIn("order_no", resp.json())

    def test_other_user_cannot_see_order(self):
        self._add_to_cart()
        create_resp = self.client.post(
            reverse("api-orders"),
            data=CHECKOUT_DATA,
            content_type="application/json",
        )
        self.assertEqual(create_resp.status_code, 201)
        order_no = create_resp.json()["order_no"]

        other = User.objects.create_user("other", password="pw")
        self.client.force_login(other)
        resp = self.client.get(reverse("api-orders-detail", args=[order_no]))
        self.assertEqual(resp.status_code, 404)
