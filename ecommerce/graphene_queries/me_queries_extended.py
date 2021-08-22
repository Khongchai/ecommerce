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
        authenticated_user = info.context.user
        cart ,_ = Cart.objects.get_or_create(customer=authenticated_user, complete=False, transaction_id=None)

        if authenticated_user.is_authenticated:
            return {"user": authenticated_user, "cart": cart}
        raise ValueError("User is not logged in")