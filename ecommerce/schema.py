#root type
#DjangoObjectType automatically generate types. We'll just have to expose them as fields now
#this is like urls.py
import graphene
from graphene_django import DjangoObjectType
from store.models import Product, DataAfterPurchase, Composer, Composition
from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations


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

"""
graphene.ObjectType gets exposed to graphql.
"""
class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    token_auth = mutations.ObtainJSONWebToken.Field()
    update_account = mutations.UpdateAccount.Field()
    refresh_token = mutations.RefreshToken.Field()

class ProductPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    skip = graphene.Int()
    is_first = graphene.Boolean()
    is_last = graphene.Boolean()
    objects = graphene.List(ProductType)

class ComposerQuery(graphene.ObjectType):
    all_composers_info = graphene.List(ComposerType)

    def resolve_all_composers(root, info):
        all_composers = Composer.objects.prefetch_related("compositions").all()
        return all_composers

class CompositionQuery(graphene.ObjectType):
    all_compositions_info = graphene.List(CompositionType)

    def resolve_all_compositions(root, info):
        all_compositions = Composition.objects.prefetch_related("composers").all() 
        return all_compositions

class Query(UserQuery, MeQuery, ComposerQuery, CompositionQuery, graphene.ObjectType):
    all_products_info = graphene.List(ProductType, search=graphene.String(required=False))
    all_products_info_paginated = graphene.Field(ProductPaginatedType)
    all_data_after_purchase_only = graphene.List(DataAfterPurchaseType)

    product_by_name = graphene.Field(ProductType, name=graphene.String(required=True))

    def resolve_all_products_info(root, info, search):
        all_products = Product.objects.select_related("authenticated_data").all()
        filtered_products = all_products.filter(name__icontains=search) if search else all_products
        return filtered_products

    def resolve_product_by_name(root, info, name):
        try:
            return Product.objects.get(name=name)
        except Product.DoesNotExist:
            return None
    
    def resolve_all_products_info_paginated(root, info):
        return "TODO"

    #hide this in prod
    def all_data_after_purchase_only(root, info):
        return DataAfterPurchase.objects.all()

class Mutation(AuthMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)


