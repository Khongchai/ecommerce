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

class CreateOrGetEmptyCartMutation(graphene.Mutation):
    class Arguments:
        pass

    cart = graphene.Field(CartType, required=True)

    @classmethod
    def mutate(cls, unused_root, info):
        """
            On page loads, if user doesn't already have a cart
            return the first empty cart with user set to current user 

            TODO => when user not logged in
        """
        del unused_root

        # top for testing, bottom for actual request
        try:
            logged_in = info.context["user"]
        except:
            logged_in = info.context.user

        if logged_in.is_anonymous:
            #TODO handle cart for user not logged in.
            raise ValueError("Handling anonymous user is not yet implemented")

        # Does not get a completed cart from the same user
        cart: Cart = Cart.objects.get_or_create(customer=logged_in, complete=False, transaction_id=None)
        return CreateOrGetEmptyCartMutation(cart=cart[0])


class CartMutation(graphene.ObjectType):
    update_cart_completion = CartCompletionMutation.Field()
    get_or_create_and_get_cart = CreateOrGetEmptyCartMutation.Field()