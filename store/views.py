from django.shortcuts import get_object_or_404

from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .models import Application, Service, Comment, Cart, CartItem, Order, OrderItem, Discount
from .serializers import AddCartItemSerializer, ApplicationSerializer, ServiceSerializer, CommentSerializer, CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, DiscountSerializer, UpdateCartItemSerializer



class ApplicationViewSet(ModelViewSet):
    serializer_class = ApplicationSerializer
    queryset = Application.objects.all()


class ServiceViewSet(ModelViewSet):
    serializer_class = ServiceSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        application_pk = self.kwargs["application_pk"]
        return Service.objects.filter(application_id=application_pk).all()
    
    def perform_create(self, serializer):
        application = get_object_or_404(Application, pk=self.kwargs['application_pk'])
        serializer.save(application=application)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        application_pk = self.kwargs["application_pk"]
        service_pk = self.kwargs["service_pk"]
        return Comment.objects.filter(service_id=service_pk, service__application_id=application_pk).all()
    
    def perform_create(self, serializer):
        service = get_object_or_404(Service, pk=self.kwargs['service_pk'])
        serializer.save(author=self.request.user, service=service)


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.prefetch_related('items__service').all()
    permission_classes = [AllowAny]


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [AllowAny]

    def get_queryset(self):
        cart_pk = self.kwargs["cart_pk"]
        return CartItem.objects.select_related('service').filter(cart_id=cart_pk).all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_pk': self.kwargs['cart_pk']}


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()


class OrderItemsViewSet(ModelViewSet):
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        order_pk = self.kwargs["order_pk"]
        return OrderItem.objects.filter(order_id=order_pk).all()


class DiscountViewSet(ModelViewSet):
    serializer_class = DiscountSerializer
    queryset = Discount.objects.all()


class DiscountServicesViewSet(ModelViewSet):
    serializer_class = ServiceSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        discount_pk = self.kwargs["discount_pk"]
        return Service.objects.filter(discounts_id=discount_pk).all()