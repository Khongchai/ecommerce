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
    me_extended = graphene.Field(UserNode)

    def resolve_me_extended(self, info):
        user = info.context.user
        if user.is_authenticated:
            return user
        return None