from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('Admin', 'Admin'),
        ('Warehouse', 'Warehouse'),
        ('Procurement', 'Procurement'),
    )
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES)
    mobile = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)




class ProductMaster(models.Model):
    PRODUCT_TYPES = [
        ('Natural', 'Natural'),
        ('Engineered', 'Engineered'),
    ]

    name = models.CharField(
        max_length=50,
        choices=PRODUCT_TYPES,
        unique=False
    )
    product_category = models.CharField(max_length=100)
    color_design = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    WAREHOUSE_CHOICES = [
        ('All','All'),
        ('Cincinnati', 'Cincinnati'),
        ('Raleigh', 'Raleigh'),
        ('Dallas', 'Dallas'),
        ('Austin', 'Austin'),
    ]
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Out of Stock', 'Out of Stock'),
        ('Not Produced', 'Not Produced'),
        ('Awaiting Stock', 'Awaiting Stock'),
    ]
    ACTION_CHOICES = [
        ('Added', 'Added'),
        ('Approve','Approve'),
        ('Reject','Reject'),
    ]
    

    product_master = models.ForeignKey(ProductMaster, on_delete=models.CASCADE, related_name="products")
    block_no = models.CharField(max_length=100)
    bundles = models.CharField(max_length=50)
    uom = models.CharField(max_length=10)
    thickness = models.DecimalField(max_digits=5, decimal_places=2)
    dimension = models.CharField(max_length=20)
    length = models.DecimalField(max_digits=10, decimal_places=2)
    width = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    note = models.TextField(null=True, blank=True)
    offer_start = models.DateTimeField()
    offer_end = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    warehouse = models.CharField(max_length=100, choices=WAREHOUSE_CHOICES)
    file = models.FileField(upload_to='product_files/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='Added')
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.product_master.name} - {self.product_master.color_design}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product}"



class Request(models.Model):
    STATUS_CHOICES = [
        ('Re Order', 'Re Order'),
        ('Product Concern', 'Product Concern'),
        ('General','General')
    ]
    raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requests')
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='General')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.raised_by.username} - {self.status}"


class Reply(models.Model):
    request = models.ForeignKey('Request', on_delete=models.CASCADE, related_name='replies')
    replied_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='replies')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.replied_by.username} at {self.created_at}"