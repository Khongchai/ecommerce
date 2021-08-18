from store.models import Product
from django.contrib import admin
from .models import Cart

class ProductInline(admin.TabularInline):
    model = Product

class CartAdmin(admin.ModelAdmin):
    inlines = [
        ProductInline,
    ]
admin.site.register(Cart, CartAdmin)
