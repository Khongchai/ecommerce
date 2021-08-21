from typing import List
from django.db.models.fields import IntegerField
from utils.get_authenticated_user import get_authenticated_user
import uuid

import graphene
from Cart.models import Cart
from ecommerce.graphene_types.model_based_types import CartType, ProductType
from store.models import Product
from users.models import CustomUser


"""
    This mutation is needed just in case the user needs to reopen cart for some reason.
"""
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

            TODO? => when user not logged in
        """
        del unused_root

        user = get_authenticated_user(info)

        if user.is_anonymous:
            #TODO? handle cart for user not logged in.
            raise ValueError("Handling anonymous user is not yet implemented")

        # Does not get a completed cart from the same user
        cart: Cart = Cart.objects.get_or_create(customer=user, complete=False, transaction_id=None)
        return CreateOrGetEmptyCartMutation(cart=cart[0])


class AddOrRemoveCartItem(graphene.Mutation):
    """
        Currently handles only authenticated users. 
    """
    class Arguments:
        product_id = graphene.Int(required=True)
        operation = graphene.String(required=True)

    products_in_cart = graphene.List(ProductType)

    @classmethod
    def mutate(cls, unused_root, info, product_id, operation):
        del unused_root

        user = get_authenticated_user(info)

        if user.is_anonymous:
            #TODO handle cart for user not logged in.
            raise ValueError("Handling anonymous user is not yet implemented")

        cart: Cart = Cart.objects.get_or_create(customer=user, complete=False, transaction_id=None)
        cart = cart[0]
        product = Product.objects.get(pk=product_id)

        if cart and product:
            cart.items_in_cart.add(product) if operation == "add" else cart.items_in_cart.remove(product)
            cart.save()
            products_in_cart = cart.items_in_cart.all()

            return AddOrRemoveCartItem(products_in_cart=products_in_cart)

        elif not cart:
            raise ValueError(f"Oops, something went wrong, this user does not have a cart attached!")
        else:
            raise ValueError(f"The product with id {product_id} does not exist")


class AddDataAfterPurchaseToUserAfterCheckout(graphene.Mutation):
    """
        Currently handles only authenticated users. 

        No need for any arguments, just attach everything in the user's cart to the user model.
    """
    class Arguments: 
        pass

    purchase_success = graphene.Boolean(required=True)

    @classmethod
    def mutate(cls, unused_root, info):
        del unused_root

        user = get_authenticated_user(info)

        if user.is_anonymous:
            #TODO handle cart for user not logged in?
            raise ValueError("Handling anonymous user is not yet implemented.")

        try:
            cart: Cart = Cart.objects.get(customer=user, complete=False, transaction_id=None)
        except:
            raise ValueError("Something's wrong; this user does not have a cart.")

        all_products_in_cart = cart.items_in_cart.all()
        compositions = [product.composition for product in all_products_in_cart]
        data_to_be_added = [composition.links for composition in compositions]
        cart.complete = True
        cart.transaction_id = uuid.uuid4() 
        cart.save()

        if cart.complete:
            for data in data_to_be_added:
                data.purchased_by.add(user) 
                data.save()

        return AddDataAfterPurchaseToUserAfterCheckout(purchase_success=True)

 
class CartMutations(graphene.ObjectType):
    update_cart_completion = CartCompletionMutation.Field()
    get_or_create_and_get_cart = CreateOrGetEmptyCartMutation.Field()
    add_or_remove_cart_item = AddOrRemoveCartItem.Field()
    add_data_after_purchase_to_user_after_checkout = AddDataAfterPurchaseToUserAfterCheckout.Field()
    
