from django.contrib import admin
from .models import DataAfterPurchase, Product, Composition, Composer

# Register your models here.
admin.site.register(DataAfterPurchase)
admin.site.register(Product)
admin.site.register(Composition)
admin.site.register(Composer)
