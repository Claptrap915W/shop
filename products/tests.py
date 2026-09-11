from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Product, Category

# Create your tests here.
class ProductListViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="test category", slug="test-cat")
        fake_image = SimpleUploadedFile("test.jpg", b"x", content_type="image/jpeg")
        fake_image2 = SimpleUploadedFile("off.jpg", b"y", content_type="image/jpeg")

        self.inactive_product=Product.objects.create(
            category=self.category,
            name="下架商品",
            slug="inactive-product",
            base_price="19.90",
            is_active=False,
            image=fake_image2,
        )

        self.active_product = Product.objects.create(
            category=self.category,
            name="上架商品",
            slug="active-product",
            base_price="29.90",
            is_active=True,
            image=fake_image,
        )

    def test_product_list_returns_paginated_results(self):
        resp = self.client.get(reverse("api-products"))
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        self.assertIn("results", body)
        self.assertIsInstance(body["results"], list)
        self.assertEqual(set(body.keys()), {"count", "next", "previous", "results"})

    def test_inactive_products_not_in_list(self):
        resp =self.client.get(reverse("api-products"))
        self.assertEqual(resp.status_code, 200)

        names = {item["name"] for item in resp.json()["results"]}
        self.assertIn("上架商品", names)
        self.assertNotIn("下架商品", names) 