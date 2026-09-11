from rest_framework import serializers

class CartItemWriteSerializer(serializers.Serializer):
    variant_id =serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, default=1)

class CartItemPatchSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)