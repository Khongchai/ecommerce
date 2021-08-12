import graphene
from graphql_auth.schema import MeQuery, UserQuery
from store.models import  DataAfterPurchase
from .graphene_types.model_based_types import  DataAfterPurchaseType
from .graphene_queries.store_queries import ComposersQuery, DataAfterPurchaseQuery, ProductsQuery, CompositionsQuery
from .graphene_queries.cart_queries import CartsQuery
from .graphene_mutations.user_mutations import AuthMutation
from .graphene_mutations.cart_mutations import CartCompletionMutation


class Query(UserQuery, MeQuery, ComposersQuery, ProductsQuery, 
            CompositionsQuery, DataAfterPurchaseQuery, 
            CartsQuery, graphene.ObjectType):
   
    all_data_after_purchase_only = graphene.List(DataAfterPurchaseType)

    
    #hide this in prod
    def all_data_after_purchase_only(root, _):
        return DataAfterPurchase.objects.all()

class Mutation(AuthMutation, CartCompletionMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)


