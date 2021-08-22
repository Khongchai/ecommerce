import graphene
from .model_based_types import CartType, ProductType, CompositionType, ComposerType
from graphql_auth.schema import UserNode


class PagePositionType(graphene.ObjectType):
    page = graphene.Int(required=True)
    of = graphene.Int(required=True)

class AllProductsDataType(graphene.ObjectType):
    products = graphene.List(ProductType, required=True)
    is_first = graphene.Boolean(required=True)
    is_last = graphene.Boolean(required=True)
    page_position = graphene.Field(PagePositionType, required=True)

class MeExtendedType(graphene.ObjectType):
    user = graphene.Field(UserNode, required=True)
    cart = graphene.Field(CartType, required=True)
