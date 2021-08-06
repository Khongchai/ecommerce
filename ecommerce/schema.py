#root type
#DjangoObjectType automatically generate types. We'll just have to expose them as fields now
#this is like urls.py

import graphene
from graphene_django import DjangoObjectType
from store.models import Product, DataAfterPurchase

from graphql_auth.schema import UserQuery, MeQuery
from graphql_auth import mutations


class ProductType(DjangoObjectType):
    class Meta: 
        model = Product
        fields = ("name", "price_usd", "image_link", "free", "authenticated_data")


class DataAfterPurchaseType(DjangoObjectType):
    class Meta: 
        model = DataAfterPurchase
        fields = ("midi_link", "wav_link", "flac_link", "pdf_link")

# class CustomRegisterFiledType(DjangoObjectType):
#     class Meta:
#         model = CustomUser
#         fields = (mutations.Register.Field(), "is_student")


class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    token_auth = mutations.ObtainJSONWebToken.Field()
    update_account = mutations.UpdateAccount.Field()
    refresh_token = mutations.RefreshToken.Field()

class Query(UserQuery, MeQuery, graphene.ObjectType):
    all_products_info = graphene.List(ProductType)
    product_by_name = graphene.Field(ProductType, name=graphene.String(required=True))

    all_data_after_purchase_only = graphene.List(DataAfterPurchaseType)

    def resolve_all_products_info(root, info):
        return Product.objects.select_related("authenticated_data").all()

    def resolve_product_by_name(root, info, name):
        try:
            return Product.objects.get(name=name)
        except Product.DoesNotExist:
            return None

    #hide this in prod
    def all_data_after_purchase_only(root, info):
        return DataAfterPurchase.objects.all()

class Mutation(AuthMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)


