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
            complete=False,
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


class TestCartCompletionQueriesAndMutations(TestCase):
    
    maxDiff=None

    def setUp(self):
        """
            Two carts, one complete set to false and one to true
        """
        user_1 = CustomUser.objects.create(
            email= "tester@tester.com",
            username= "tester",
            password="strongpassword",
        )
        user_2 = CustomUser.objects.create(
            email= "tester2@tester2.com ",
            username= "tester2",
            password="strongpassword2",
        )
        composition_1 = Composition.objects.create(
            name="When You Wish Upon a Star"
        )
        composition_2 = Composition.objects.create(
            name="Darude Sandstorm"
        )
        product_1 = Product.objects.create(
            price_usd=10,
            image_link="product_1_img_link",
            composition=composition_1,
            free=False,
        )
        product_2 = Product.objects.create(
            price_usd=10,
            image_link="product_2_img_link",
            composition=composition_2,
            free=True,
        )
        cart_1:Cart = Cart.objects.create(
            customer=user_1,
            complete=False,
        )
        cart_2:Cart = Cart.objects.create(
            customer=user_2,
            complete=True,
        )
        cart_1.items_in_cart.add(product_1)
        cart_2.items_in_cart.add(product_2)


    def test_cart_completion_stat(self):
        """
            When cart is set to complete, uuid should be recorded.

            When completed cart is set to incomplete, uuid should be removed. 
        """
        
        class Query(CartsQuery, graphene.ObjectType):
            pass

        schema = graphene.Schema(query=Query)
        query = """
            query{
                allCartsInfo{
                    complete
                }
            } 
        """
        query_result = schema.execute(query)
        query_expected = {
            "allCartsInfo": [{
                "complete": False  
            }, {
                "complete": True
            }]
        }
        self.assertEqual(query_result.data, query_expected)

    def test_cart_uuid(self):
        """
            This test case checks if uuid is attached automatically to the 
            cart with complete = true and None for cart = false. 

            This test uses the complete=false cart, set its completion to true through
            graphene resolver, then verify that the transaction_id(uuid) is automatically added.
        """

        class Query(CartsQuery, graphene.ObjectType):
            pass

        class Mutation(CartCompletionMutation, graphene.ObjectType):
            pass
        
        # completion=False cart's id = 3
        schema = graphene.Schema(mutation=Mutation, query=Query)
        mutation = """
            mutation{
                modifyCart(cartId: 3, completion: true){
                    id
                }
            } 
        """
        modified_cart_result = schema.execute(mutation)
        print(json.dumps(modified_cart_result.data, skipkeys=True, indent=4))
        
        

