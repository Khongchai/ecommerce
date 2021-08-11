import graphene
from .model_based_types import ProductType

class PagePositionType(graphene.ObjectType):
    page = graphene.Int(required=True)
    of = graphene.Int(required=True)

class AllProductsDataType(graphene.ObjectType):
    products = graphene.List(ProductType, required=True)
    is_first = graphene.Boolean(required=True)
    is_last = graphene.Boolean(required=True)
    page_position = graphene.Field(PagePositionType, required=True)
