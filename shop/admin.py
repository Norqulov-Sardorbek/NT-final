from django.contrib import admin
from django.utils.html import format_html
from .models import *
from django.urls import reverse
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from click_up.models import ClickTransaction
from django.contrib.auth.models import Group

admin.site.site_header = 'E-Commerce Admin'


class ImageProductsInline(admin.TabularInline):
    model = ImageProducts
    extra = 1


class ProductsAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "discount", "quantity", "category", "product_image")
    inlines = [ImageProductsInline]

    def product_image(self, obj):
        first_image = obj.images.first()
        if first_image and first_image.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;" />',
                               first_image.image.url)
        return "No Image"

    product_image.short_description = "Rasm:"




class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    exclude = ('total_price',)
    readonly_fields = ('product', 'quantity', 'calculated_total_price', "product_image",)


    def calculated_total_price(self, obj):
        return obj.quantity * obj.product.discounted_price

    calculated_total_price.short_description = "Jami narxi:"

    def product_image(self, obj):
        if obj and obj.product and obj.product.images.exists():
            first_image = obj.product.images.first()
            return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;" />',
                               first_image.image.url)
        return "No Image"

    product_image.short_description = "O'yinchoq rasmi:"


class OrderAdmin(admin.ModelAdmin):
    list_display = (
         "ordered_by_name", "address", "total_price", "payment_method", "is_paid", "status")
    list_filter = ("is_paid", "payment_method")
    search_fields = ("ordered_by__first_name", "ordered_by__username", "address")
    ordering = ("-created_at",)
    inlines = [OrderItemInline]
    readonly_fields = ('buyer_name','buyer_surname','phone_number',
        "ordered_by", "address", "total_price", "payment_method", "is_paid",   "created_at")

    def ordered_by_name(self, obj):
        return obj.ordered_by.first_name if obj.ordered_by else "No User"

    ordered_by_name.short_description = "Ordered By"



admin.site.register(Category)
admin.site.register(Products, ProductsAdmin)
admin.site.register(Order, OrderAdmin)

admin.site.unregister(Group)
admin.site.unregister(BlacklistedToken)
admin.site.unregister(OutstandingToken)
admin.site.unregister(ClickTransaction)
