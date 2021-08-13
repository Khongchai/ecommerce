import graphene
from Cart.models import Cart
from ecommerce.graphene_types.model_based_types import CartType

class CartsQuery(graphene.ObjectType):
    all_carts_info = graphene.List(CartType)

    def resolve_all_carts_info(root, _):
        all_carts = Cart.objects.prefetch_related("items_in_cart").all()
        return all_carts