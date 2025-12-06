from django.contrib import admin
from .models import Customer, Application, Discount, Service, Comment, Cart, CartItem, Order, OrderItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user", "phone_number"]


class ServiceInline(admin.TabularInline):
    model = Service
    fields = ["name", "application", "slug", "description", "price", "discounts"]
    extra = 1


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["title", "description", "top_service"]
    inlines = [ServiceInline]


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ["discount_percent", "code", "name"]


class CommentsInline(admin.TabularInline):
    model = Comment
    fields = ["author", "service", "body", "status"]
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "application", "description", "price", "datetime_created", "discounts"]
    inlines = [CommentsInline]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("datetime_created",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["author", "service", "body", "status", "datetime_created"]


class CartItemInline(admin.TabularInline):
    model = CartItem
    fields = ["cart", "service"]
    extra = 1


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "datetime_created"]
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["cart", "service"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ["order", "service", "price"]
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["customer", "datetime_created", "status"]
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "service", "price"]