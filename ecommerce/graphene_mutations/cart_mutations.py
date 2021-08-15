import uuid

import graphene
from Cart.models import Cart
from ecommerce.graphene_types.model_based_types import CartType


class CartCompletionMutation(graphene.Mutation):
    class Arguments:
        cart_id = graphene.ID()
        completion = graphene.Boolean()

    modify_cart = graphene.Field(CartType, cart_id=graphene.Int(), completion=graphene.Boolean())

    @classmethod
    def mutate(cls, unused_root, unused_info, cart_id, completion):
        """
            On completion, set transaction id
            On completion remove, remove transaction id 
        """
        del unused_root, unused_info
        cart: Cart = Cart.objects.get(id=cart_id)
        cart.complete = completion
        cart.transaction_id = uuid.uuid4() if completion else None
        cart.save()

        return CartCompletionMutation(cart=cart)

class CartMutation(graphene.ObjectType):
    update_cart_completion = CartCompletionMutation.Field()