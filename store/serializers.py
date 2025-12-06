from django.conf import settings
from django.utils.safestring import mark_safe

from rest_framework import serializers

from .models import Application, Service, Comment, Cart, CartItem, Order, OrderItem, Discount


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["title", "description", "top_service"]


class ServiceSerializer(serializers.ModelSerializer):
    discounted_price = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True, required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ["id", "name", "description", "price", "discounts", "discounted_price", "image", "image_url"]
    
    def get_discounted_price(self, obj):
        return obj.get_discounted_price()
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        path = obj.image.url if obj.image and hasattr(obj.image, 'url') else settings.MEDIA_URL + 'services/images/default_service.jpg'
        if request is not None:
            return request.build_absolute_uri(path)
        else:
            base_url = 'http://127.0.0.1:8000'
            return base_url + path
    
    def update(self, instance, validated_data):
        if 'image' in validated_data and validated_data['image'] is None:
            validated_data.pop('image')
        return super().update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["author", "body", "datetime_created"]
        read_only_fields = ["author"]


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]


class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "service", "quantity"]
    
    def create(self, validated_data):
        cart_id = self.context['cart_pk']
        service = validated_data.get('service')
        quantity = validated_data.get('quantity')

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, service_id=service.id)
            cart_item.quantity += quantity
            cart_item.save()
            return cart_item
        except CartItem.DoesNotExist:
            return CartItem.objects.create(cart_id=cart_id, **validated_data)


class CartItemSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    item_total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "service", "quantity", "item_total_price"]

    def get_item_total_price(self, obj):
        return obj.get_item_total_price()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "datetime_created", "items", "total_cart_price"]
        read_only_fields = ["id"]

    def get_total_cart_price(self, obj):
        return obj.get_total_price()


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["customer", "datetime_created", "status"]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "service", "price"]


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ["id", "name", "discount_percent"]