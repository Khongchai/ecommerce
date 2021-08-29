from Cart.models import Cart
from ecommerce.graphene_types.custom_types import MeExtendedType
import graphene 
from graphql_auth.schema import UserNode

"""
    TODO: return UserNode along side the related fields of the user (like the user's cart and product he/she owns
        but just do cart for now 
    )
"""

class MeQueryExtended(graphene.ObjectType):
    """
        MeQuery, but with arbitrary related fields attached. 
    """
    me_extended = graphene.Field(MeExtendedType)

    def resolve_me_extended(self, info):
        user = info.context.user
        if user.is_anonymous:
            return None
            
        cart ,_ = Cart.objects.get_or_create(customer=user, complete=False, transaction_id=None)

        return {"user": user, "cart": cart}