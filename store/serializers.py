from rest_framework import serializers

from .models import Application, Service, Comment, Cart, CartItem, Order, OrderItem, Discount


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["title", "description", "top_service"]


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "name", "description", "price"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["author", "body", "datetime_created"]


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

    def get_item_total_price(self, cart_item):
        return cart_item.quantity * cart_item.service.price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "datetime_created", "items", "total_cart_price"]
        read_only_fields = ["id"]

    def get_total_cart_price(self, cart):
        return sum(item.quantity * item.service.price for item in cart.items.all())


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
        fields = ["id", "name"]