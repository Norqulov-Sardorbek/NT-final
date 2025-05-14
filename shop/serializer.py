import requests
from rest_framework import serializers
from django.contrib.auth import get_user_model
from decouple import config
from .models import *
from rest_framework.serializers import Serializer, IntegerField
User = get_user_model()


class ImageProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageProducts
        fields = ["image"]

class CommentProductSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(required=False, allow_blank=True)
    rating = serializers.IntegerField(required=False)
    first_name = serializers.ReadOnlyField(source="commented_by.first_name")

    class Meta:
        model = CommentProducts
        fields = ["comment", "rating", "product", "first_name", "created_at"]
        extra_kwargs = {
            'commented_by': {'read_only': True},
            'product': {'read_only': True},
        }

    def create(self, validated_data):
        request = self.context.get("request")
        if request:
            validated_data["user"] = request.user
        return super().create(validated_data)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'gender', 'name', 'product_count']




class ProductsSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    comments = CommentProductSerializer(many=True, read_only=True)

    class Meta:
        model = Products
        fields = [
            "id", "name", "price", "images", "description",
            "discount", "quantity", "category", "discounted_price",
            "average_rating", "sold", "video_url","comments"
        ]

    def get_images(self, obj):
        return [
            self._make_https(img.image.url)
            for img in obj.images.all()
        ]

    def _make_https(self, url):
        if url.startswith("http://"):
            return url.replace("http://", "https://")
        return url



class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Products.objects.all(), write_only=True)
    product_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'product_detail', 'quantity']

    def get_product_detail(self, obj):
        request = self.context.get("request")
        lang = request.query_params.get("lang") if request else None

        product = obj.product
        first_image = product.images.first()
        image_url = first_image.image.url if first_image else None

        if lang == "ru":
            title = product.name_ru
        elif lang == "en":
            title = product.name_en
        else:
            title = product.name

        return {
            "id": product.id,
            "title": title,
            "price": product.price,
            "image": image_url
        }

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    ordered_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Order
        fields ='__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        if not validated_data.get('ordered_by') and request:
            validated_data['ordered_by'] = request.user
        user = request.user
        user.first_name = validated_data.get('buyer_name')
        user.last_name = validated_data.get('buyer_surname')
        user.address = validated_data.get('address')
        user.save()
        items_data = validated_data.pop('items')
        order = Order.objects.create( **validated_data)
        for item_data in items_data:
            product = item_data.get("product")
            quantity = item_data.get("quantity", 1)
            price = product.discounted_price if product else 0

            total_price = quantity * price


            OrderItem.objects.create(order=order, total_price=total_price, **item_data)

        return order




class LikedProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikedProducts
        fields = "__all__"





class PermissionToCommentSerializer(Serializer):
    product_id = IntegerField()

