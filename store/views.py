from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from rest_framework import status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ModelViewSet, ReadOnlyModelViewSet, ViewSet
from rest_framework.decorators import action

from .models import Application, Customer, Service, Comment, Cart, CartItem, Order, OrderItem, Discount
from .serializers import AddCartItemSerializer, ApplicationSerializer, CustomerSerializer, OrderCreateSerializer, OrderForAdminSerializer, ServiceSerializer, CommentSerializer, CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, DiscountSerializer, UpdateCartItemSerializer



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
    http_method_names = ['get', 'post', 'head', 'options']

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Order.objects.prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('service'))
        ).select_related('customer__user')

        if self.request.user.is_staff:
            return queryset
        return queryset.filter(customer__user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderCreateSerializer
        
        if self.request.user.is_staff:
            return OrderForAdminSerializer
            
        return OrderSerializer

    def get_serializer_context(self):
        return {"user": self.request.user}

    def create(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)

        if not customer.phone_number:
            return Response(
                {
                    "error": "phone_number_required",
                    "message": "You must enter a phone number to place an order. Please register your phone number first.",
                    "redirect_url": request.build_absolute_uri("/customers/me/")
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = OrderCreateSerializer(
            data=request.data,
            context={'user': request.user}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)


class OrderItemsViewSet(ReadOnlyModelViewSet):
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        order_pk = self.kwargs["order_pk"]
        return OrderItem.objects.select_related('service').filter(order_id=order_pk)


class DiscountViewSet(ModelViewSet):
    serializer_class = DiscountSerializer
    queryset = Discount.objects.all()


class DiscountServicesViewSet(ModelViewSet):
    serializer_class = ServiceSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        discount_pk = self.kwargs["discount_pk"]
        return Service.objects.filter(discounts_id=discount_pk).all()


class CustomerViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

    def list(self, request):
        if request.user.is_staff:
            queryset = Customer.objects.all()
        else:
            queryset = Customer.objects.filter(user=request.user)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        if not request.user.is_staff:
            raise PermissionDenied("Normal users do not have permission to access this address. Use '/custommers/me/'.")

        customer = get_object_or_404(Customer, pk=pk)
        serializer = self.get_serializer(customer)
        return Response(serializer.data)

    @action(detail=False, methods=['GET', 'PATCH', 'PUT'], url_path='me')
    def me(self, request):
        customer = Customer.objects.get(user=request.user)

        if request.method == 'GET':
            serializer = self.get_serializer(customer)
            return Response(serializer.data)

        serializer = self.get_serializer(customer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)