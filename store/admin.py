from django.contrib import admin
from .models import DataAfterPurchase, Product, Composition, Composer

# Register your models here.
admin.site.register(Product)


class ProductInline(admin.TabularInline):
    model = Product

class DataAfterPurchaseInline(admin.TabularInline):
    model = DataAfterPurchase

@admin.register(Composition)
class CompositionAdmin(admin.ModelAdmin):
    inlines = [DataAfterPurchaseInline, ProductInline]


class CompositionInline(admin.TabularInline):
    model = Composition.composers.through

@admin.register(Composer)
class ComposerAdmin(admin.ModelAdmin):
    """
        Composer admin. 
    """
    inlines = [
        CompositionInline,
    ]
