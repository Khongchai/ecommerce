import uuid

import graphene
from Cart.models import Cart
from ecommerce.graphene_types.model_based_types import CartType, ProductType
from store.models import Product
from users.models import CustomUser


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

"""
    This mutation is currently superfluous,
    on prod if still not used, remove.
"""
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


class AddOrRemoveCartItem(graphene.Mutation):
    """
        Currently handles only authenticated users. 
    """
    class Arguments:
        product_id = graphene.Int()

    #On success, returns the added product or simply return true if user removes a product
    added_product = graphene.Field(ProductType)

    @classmethod
    def mutate(cls, unused_root, info, product_id):
        del unused_root

        try:
            logged_in = info.context["user"]
        except:
            logged_in = info.context.user

        if logged_in.is_anonymous:
            #TODO handle cart for user not logged in.
            raise ValueError("Handling anonymous user is not yet implemented")
        
        cart: Cart = Cart.objects.get_or_create(customer=logged_in, complete=False, transaction_id=None)
        product_to_be_added = Product.objects.get(pk=product_id)

        if cart and product_to_be_added:
            cart.items_in_cart.add(product_to_be_added)
            cart.save()
        elif not cart:
            raise ValueError(f"Oops, something went wrong, this user does not have a cart attached!")
        else:
            raise ValueError(f"The product with id {product_id} does not exist")

 
class CartMutations(graphene.ObjectType):
    update_cart_completion = CartCompletionMutation.Field()
    get_or_create_and_get_cart = CreateOrGetEmptyCartMutation.Field()
    add_or_remove_cart_item = AddOrRemoveCartItem.Field()
