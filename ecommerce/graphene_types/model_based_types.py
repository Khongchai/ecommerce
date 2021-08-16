import graphene
from Cart.models import Cart
from graphene_django import DjangoObjectType
from store.models import Composer, Composition, DataAfterPurchase, Product


class ProductType(DjangoObjectType):
    class Meta: 
        model = Product
        fields = "__all__"

class CompositionType(DjangoObjectType):
    class Meta: 
        model = Composition
        fields = "__all__"

class ComposerType(DjangoObjectType):
    class Meta: 
        model = Composer
        fields = "__all__"

class DataAfterPurchaseType(DjangoObjectType):
    class Meta: 
        model = DataAfterPurchase
        fields = "__all__"

class CartType(DjangoObjectType):
    class Meta:
        model = Cart
        fields = "__all__" 