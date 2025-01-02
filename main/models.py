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
    CATEGORY_CHOICES = [
        ('Granite', 'Granite'),
        ('Marble', 'Marble'),
        ('Quarzite', 'Quarzite'),
        ('Dolomite', 'Dolomite'),
        ('Onyx', 'Onyx'),
        ('Quartz', 'Quartz'),
        ('Porcelain', 'Porcelain'),
        ('Semi-Precious', 'Semi-Precious'),
        ('Printed Quartz', 'Printed Quartz')
    ]

    WAREHOUSE_CHOICES = [
        ('All', 'All'),
        ('Cincinnati', 'Cincinnati'),
        ('Raleigh', 'Raleigh'),
        ('Dallas', 'Dallas'),
        ('Austin', 'Austin'),
    ]

    STATUS_CHOICES = [
        ('PI Received', 'P.I Received'),
        ('PO Raised', 'P.O Raised'),
        ('In Production', 'In Production'),
        ('Container No', 'Container No'),
        ('ETD from Origin Port', 'ETD from Origin Port'),
        ('On-Water', 'On-Water'),
        ('ETA: US Port', 'ETA: US Port'),
    ]

    ACTION_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, blank=True, null=True)
    color_design = models.CharField(max_length=100, null=True)
    block_no = models.CharField(max_length=100)
    bundles = models.CharField(max_length=50)
    thickness = models.DecimalField(max_digits=5, decimal_places=2)
    length = models.DecimalField(max_digits=10, decimal_places=2)
    width = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    note = models.TextField(null=True, blank=True)
    offer_start = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    warehouse = models.CharField(max_length=100, choices=WAREHOUSE_CHOICES)
    file = models.FileField(upload_to='product_files/', null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PI Received')
    status_text = models.TextField(null=True, blank=True) 
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='Pending')
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.category} - {self.color_design}"



class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product}"



class Request(models.Model):
    STATUS_CHOICES = [
        ('Product Concern', 'Product Concern'),
        ('General', 'General')
    ]
    
    raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requests')
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='General')
    subject = models.CharField(max_length=220, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.raised_by.username} - {self.status} - {self.sub_option}"


class Reply(models.Model):
    request = models.ForeignKey('Request', on_delete=models.CASCADE, related_name='replies')
    replied_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='replies')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.replied_by.username} at {self.created_at}"  


class Reorder(models.Model):
    CATEGORY_CHOICES = [
        ('Granite', 'Granite'),
        ('Marble', 'Marble'),
        ('Quarzite','Quarzite'),
        ('Dolomite','Dolomite'),
        ('Onyx','Onyx'),
        ('Quartz', 'Quartz'),
        ('Porcelain', 'Porcelain'),
        ('Semi-Precious','Semi-Precious'),
        ('Printed Quartz','Printed Quartz')    
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    color = models.CharField(max_length=220)
    thickness = models.DecimalField(max_digits=5, decimal_places=2)
    bundles = models.IntegerField()

