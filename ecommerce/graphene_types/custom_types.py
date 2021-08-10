import graphene
from .model_based_types import ProductType

class PagePositionType(graphene.ObjectType):
    page = graphene.Int()
    of = graphene.Int()

class AllProductsDataType(graphene.ObjectType):
    products = graphene.List(ProductType)
    is_first = graphene.Boolean()
    is_last = graphene.Boolean()
    page_position = graphene.Field(PagePositionType)
