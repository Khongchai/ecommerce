from django.contrib import admin
from .models import CustomUser
from store.models import DataAfterPurchase

class PurchasedProductInline(admin.TabularInline):
    model = DataAfterPurchase.purchased_by.through

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    inlines = [PurchasedProductInline,]
