import graphene
from graphql_auth.schema import MeQuery, UserQuery
from store.models import  DataAfterPurchase, Product
from .graphene_types.model_based_types import  DataAfterPurchaseType, ProductType
from .graphene_queries.queries import ComposersQuery, DataAfterPurchaseQuery, ProductsQuery, CompositionsQuery
from .graphene_mutations.mutations import AuthMutation


class Query(UserQuery, MeQuery, ComposersQuery, ProductsQuery, CompositionsQuery, DataAfterPurchaseQuery, graphene.ObjectType):
   
    all_data_after_purchase_only = graphene.List(DataAfterPurchaseType)
    product_by_name = graphene.Field(ProductType, name=graphene.String(required=True))
    def resolve_product_by_name(root, _, name):
        try:
            return Product.objects.get(name=name)
        except Product.DoesNotExist:
            return None
    
    #hide this in prod
    def all_data_after_purchase_only(root, _):
        return DataAfterPurchase.objects.all()

class Mutation(AuthMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)


