from django.urls import path
from .views import *

urlpatterns = [
    path('categories/', CategoryListAPIView.as_view(), name='categories'),
    path('category-create/', CreateCategoryAPIView.as_view(), name='category-create'),
    path('category-update/<int:category_id>/',UpdateCategoryAPIView.as_view(), name='update_category'),
    path('category-delete/<int:category_id>/',DeleteCategoryAPIView.as_view(), name='delete_category'),
    path('products/', ProductListAPIView.as_view(), name='products'),
    path('product-create/', CreateProductAPIView.as_view(), name='product-create'),
    path('products/<int:category_id>/', ProductListAPIView.as_view(), name='product-list'),
    path('products-update/<int:product_id>/', UpdateProductAPIView.as_view(), name='products-update'),
    path('products-delete/<int:product_id>/', DeleteProductAPIView.as_view(),name='products-delete'),
    path('new-products/',PopularProducts.as_view(), name='popular-products'),
    path('product-details/<int:product_id>/', ProductDetailsAPIView.as_view(), name='product-details'),
    path('comment-create/<int:product_id>/', CommentProductAPIView.as_view(), name='comment-create'),
    path('comment-permission/<int:product_id>/', PermissionToCommentAPIView.as_view(), name='comment-premission'),
    path('order-product/', OrderCreateAPIView.as_view(), name='order-product'),
    path('order-history/',GetOrderHistoryAPIView.as_view(), name='order-history'),
]
