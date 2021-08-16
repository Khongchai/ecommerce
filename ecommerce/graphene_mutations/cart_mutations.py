import uuid

import graphene
from Cart.models import Cart
from users.models import CustomUser
from ecommerce.graphene_types.model_based_types import CartType


class CartCompletionMutation(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        completion = graphene.Boolean()

    cart = graphene.Field(CartType)

    @classmethod
    def mutate(cls, unused_root, unused_info, username, completion):
        """
            On completion, set transaction id
            On completion remove, remove transaction id 
        """
        del unused_root, unused_info
        user = CustomUser.objects.get(username=username)
        cart: Cart = Cart.objects.get(customer=user)
        cart.complete = completion
        cart.transaction_id = uuid.uuid4() if completion else None
        cart.save()

        return CartCompletionMutation(cart=cart)

class CartMutation(graphene.ObjectType):
    update_cart_completion = CartCompletionMutation.Field()