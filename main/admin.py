from django.contrib import admin
from main.models import *
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(ProductMaster)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Request)
