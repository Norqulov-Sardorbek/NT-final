from decimal import Decimal
from django.db.models import Avg, Sum
from django.contrib.auth import get_user_model
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_delete
import cloudinary.uploader
from cloudinary.models import CloudinaryField
# Create your models here.


User = get_user_model()

class Category(models.Model):

    name:str = models.CharField(max_length=100,default='ok',verbose_name='Kategory nomi (uzb)')

    @property
    def product_count(self):
        return self.products.count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"


class Products(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategoriya:",related_name="products")
    name = models.CharField(max_length=100,default='ok', verbose_name="O'yinchoq nomi (uzb):")
    price = models.DecimalField(decimal_places=2, max_digits=14, verbose_name="O'yinchoq narxi (Faqat so'mda):")
    discount = models.IntegerField(default=0, verbose_name="O'yinchoq chegirmasi: (ixtiyoriy)")
    description = models.TextField(null=True, blank=True, verbose_name="O'yinchoq xaqida (uzb):")
    quantity = models.IntegerField(verbose_name="O'yinchoq soni:")
    video_url = models.URLField(null=True, blank=True, verbose_name="You tubdan video joylash:")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)



    @property
    def discounted_price(self):
        if self.discount > 0:
            discounted = self.price * Decimal(1 - self.discount / 100)
            return Decimal(f'{discounted}').quantize(Decimal('0.00'))
        return Decimal(f'{self.price}').quantize(Decimal('0.00'))

    def average_rating(self):
        avg_rating = self.comments.aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 1) if avg_rating else 0

    def sold(self):
        return self.ordered_products.aggregate(Sum("quantity"))[
            "quantity__sum"] or 0

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"


class ImageProducts(models.Model):
    product = models.ForeignKey(Products, related_name="images", on_delete=models.CASCADE)
    image = CloudinaryField("image")

    class Meta:
        verbose_name = "Rasm"
        verbose_name_plural = "Rasmlar"


@receiver(post_delete, sender=ImageProducts)
def delete_product_image(sender, instance, **kwargs):
    if instance.image:
        try:
            cloudinary.uploader.destroy(instance.image.public_id)
        except Exception as e:
            print(f"Cloudinary rasm o‘chirishda xatolik: {e}")


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('delivering','Yetkazilmoqda'),
        ('delivered', 'Yetkazib berildi'),
        ('cancelled', 'Bekor qilindi'),

    ]
    PAYMENT_METHOD_CHOICES = [
        ('naxt', 'Naxt'),
        ('karta', 'Karta'),
    ]

    buyer_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Xaridor ismi:')
    buyer_surname = models.CharField(max_length=100, null=True, blank=True, verbose_name='Xaridor familiyasi:')
    phone_number = models.CharField(max_length=100, null=True, blank=True, verbose_name='Xaridor raqami:')
    ordered_by = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    address = models.TextField(verbose_name='Xaridor manzili:')
    total_price = models.DecimalField(decimal_places=2, max_digits=14, default=0, verbose_name='Jami xarid narxi:')
    payment_method = models.CharField(choices=PAYMENT_METHOD_CHOICES, max_length=6, default='naxt',
                                      verbose_name='Tolov turi:')
    payment_link = models.URLField(blank=True, null=True, verbose_name='Tolov qilish uchun link:')
    is_paid = models.BooleanField(default=False, verbose_name='Tolanganligi:')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Buyurtma xolati:')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Xarid qilingan vaqt:')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ordered by {self.buyer_name}"

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="ordered_products",verbose_name="O'yinchoq nomi:")
    quantity = models.PositiveIntegerField(default=1, verbose_name='Buyurtma soni:')
    total_price = models.DecimalField(decimal_places=2, max_digits=14, default=0, verbose_name='Jami summa:')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Buyurtmadagi o'yinchoq"
        verbose_name_plural = "Buyurtmadagi o'yinchoqlar"

    def __str__(self):
        return self.product.name


class CommentProducts(models.Model):
    product = models.ForeignKey(Products, related_name="comments", on_delete=models.CASCADE)
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    rating = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class LikedProducts(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE)

