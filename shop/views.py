from django.shortcuts import  get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import *
from rest_framework.pagination import PageNumberPagination
# Create your views here.


class CategoryPagination(PageNumberPagination):
    page_size = 100


class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductsSerializer

    def get_queryset(self):
        category_id = self.kwargs.get("category_id")
        queryset = Products.objects.prefetch_related("images")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

class CreateProductAPIView(generics.CreateAPIView):
    serializer_class = ProductsSerializer
    queryset = Products.objects.all()
class CreateCategoryAPIView(generics.CreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

class ProductDetailsAPIView(generics.RetrieveAPIView):
    serializer_class = ProductsSerializer
    queryset = Products.objects.all()

    def get_object(self):
        product_id = self.kwargs.get("product_id")
        return get_object_or_404(Products, pk=product_id)


class CategoryListAPIView(generics.ListAPIView):
    serializer_class = CategorySerializer
    pagination_class = CategoryPagination

    def get_queryset(self):
        gender = self.request.query_params.get("gender")
        if gender:
            return Category.objects.filter(gender=gender)
        return Category.objects.all()


class PopularProducts(APIView):
    serializer_class = ProductsSerializer

    def get(self, request):
        popular_products = Products.objects.order_by("-created_at")[:8]
        serializer = self.serializer_class(popular_products, many=True, context={'request': request})
        return Response(serializer.data)


class CommentProductAPIView(APIView):
    serializer_class = CommentProductSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs.get("product_id")
        product = get_object_or_404(Products, id=product_id)
        comment = request.data.get("comment")
        rating = request.data.get("rating")

        data = {
            "product": product,
            "comment": comment,
            "rating": rating,
        }

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(commented_by=request.user,product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class OrderCreateAPIView(generics.CreateAPIView):
    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        for item in order.items.all():
            product = item.product
            product.quantity -= item.quantity
            product.save(update_fields=["quantity"])
        result = {"order": serializer.data}
        return Response(result, status=status.HTTP_201_CREATED)

class UpdateProductAPIView(generics.UpdateAPIView):
    serializer_class = ProductsSerializer
    permission_classes = [IsAuthenticated]
    def put(self, request, *args, **kwargs):
        product_id = self.kwargs.get("product_id")
        product = get_object_or_404(Products, id=product_id)
        serializer = self.serializer_class(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        result = {"product": serializer.data}
        return Response(result, status=status.HTTP_200_OK)

class DeleteProductAPIView(generics.DestroyAPIView):
    serializer_class = ProductsSerializer
    permission_classes = [IsAuthenticated]
    def delete(self, request, *args, **kwargs):
        product_id = self.kwargs.get("product_id")
        product = get_object_or_404(Products, id=product_id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class PermissionToCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')

        user_id = request.user.id
        exists = Order.objects.filter(
            ordered_by_id=user_id,
            status="delivered",
            items__product_id=product_id
        ).exists()

        if exists:
            return Response({"message": True}, status=status.HTTP_200_OK)

        return Response({"message": False}, status=status.HTTP_403_FORBIDDEN)

class UpdateCategoryAPIView(generics.UpdateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    def put(self, request, *args, **kwargs):
        category_id = self.kwargs.get("category_id")
        category = get_object_or_404(Category, id=category_id)
        serializer = self.serializer_class(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        result = {"category": serializer.data}
        return Response(result, status=status.HTTP_200_OK)

class DeleteCategoryAPIView(generics.DestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    def delete(self, request, *args, **kwargs):
        category_id = self.kwargs.get("category_id")
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class GetOrderHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializers = OrderSerializer

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        orders = Order.objects.filter(
            ordered_by_id=user_id,
        )
        serializer = OrderSerializer(orders, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
