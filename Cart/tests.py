import json
import uuid

import graphene
from django.test import TestCase, testcases
from ecommerce.graphene_mutations.cart_mutations import CartCompletionMutation
from ecommerce.graphene_queries.cart_queries import CartsQuery
from ecommerce.graphene_queries.store_queries import ProductsQuery
from store.models import Composition, Product
from users.models import CustomUser

from .models import Cart


# Create your tests here.
class TestCartQueries(TestCase):
    maxDiff = None

    def setUp(self):
        user_1 = CustomUser.objects.create(
            email= "tester@tester.com",
            username= "tester",
            password="strongpassword",
        )
        composition_1 = Composition.objects.create(
            name="When You Wish Upon a Star"
        )
        product_1 = Product.objects.create(
            price_usd=10,
            image_link="product_1_img_link",
            composition=composition_1,
            free=False,
        )
        cart:Cart = Cart.objects.create(
            customer=user_1,
        )
        cart.items_in_cart.add(product_1)

    def test_cart_customer_product_relationships(self):

        class Query(CartsQuery, graphene.ObjectType):
            pass

        schema = graphene.Schema(query=Query)
        query = """
            query{
                allCartsInfo{
                    itemsInCart{
                        composition{
                            name
                        }
                    }
                }
            } 
        """
        expected = {
            "allCartsInfo": [
                {
                    "itemsInCart": [{
                        "composition": {
                            "name": "When You Wish Upon a Star"
                        }
                    }]
                }
            ]
        }

        query_result = schema.execute(query)
        self.assertEqual(query_result.data, expected)


class TestCartMutations(TestCase):
    
    maxDiff=None

    def test_set_cart_status(self):
        """
            When cart is set to complete, uuid should be recorded.

            When completed cart is set to incomplete, uuid should be removed. 
        """
        
        class Query(CartsQuery, graphene.ObjectType):
            pass

        class Mutation(CartCompletionMutation, graphene.ObjectType):
            pass

        schema = graphene.Schema(query=Query, mutation=Mutation)
        query = """
            query{
                allCartsInfo{
                    complete
                }
            } 
        """
        # schema.execute(query)
        # print(query)
        # query_expected = {
        #     "allCartsInfo": {
        #         "complete": True
        #     }
        # }
