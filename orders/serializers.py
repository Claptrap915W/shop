from rest_framework import serializers
from .models import Order, OrderItem, Payment

class CheckoutWriteSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    address = serializers.CharField()
    card_number = serializers.CharField(max_length=19)
    card_expiry = serializers.CharField(max_length=7)
    card_cvc = serializers.CharField(max_length=4)

    def validate_card_number(self, value):
        card = value.replace(' ', '')
        if not card.isdigit() or len(card) < 13:
            raise serializers.ValidationError('Invalid card number.')
        return card

    def get_payment_data(self):
        card = self.validated_data['card_number']
        return {
            'method': 'credit_card',
            'card_last_four': card[-4:],
        }

    def get_shipping_data(self):
        data = self.validated_data
        return {
            'full_name': data['full_name'],
            'email': data['email'],
            'phone': data['phone'],
            'address': data['address'],
        }

class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["order_no", "total", "status","created_at" ]
        read_only_fields = fields

class OrderItemSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["product_name", "color_name", "size", "subtotal", "quantity", "image_url"]
    
    def get_image_url(self, obj):
        if not obj.image_path:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image_url) if request else obj.image_url

class PaymentSerializer(serializers.ModelSerializer):
    method_display = serializers.CharField(source='get_method_display', read_only=True)

    class Meta:
        model = Payment
        fields = ["transaction_id","method", "method_display", "card_last_four", "paid_at"]

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ["order_no", "total", "status", "status_display", "full_name", "email", "phone", "address", "created_at","items", "payment"]
        read_only_fields = fields