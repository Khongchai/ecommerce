from store.models import DataAfterPurchase
import uuid

import graphene
from django.test import TestCase
from ecommerce.graphene_mutations.cart_mutations import CartMutations
from ecommerce.graphene_mutations.user_mutations import AuthMutation
from ecommerce.graphene_queries.cart_queries import CartsQuery
from graphene.test import Client
from graphene_django.utils.testing import GraphQLTestCase
from store.models import Composer, Composition, Product
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


class TestCartCompletionQueriesAndMutations(GraphQLTestCase):
    
    maxDiff=None

    def setUp(self):
       
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
        )
        product_2 = Product.objects.create(
            price_usd=10,
            image_link="product_2_img_link",
            composition=composition_2,
        )
        cart_1:Cart = Cart.objects.create(
            customer=user_1,
            complete=False,
        )
        cart_2:Cart = Cart.objects.create(
            customer=user_2,
            complete=True,
            transaction_id=uuid.uuid4()
        )
        cart_1.items_in_cart.add(product_1)
        cart_2.items_in_cart.add(product_2)


    def test_cart_completion_stats(self):
        #Given two carts of different completion stats,

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

        #when fetched,
        query_expected = {
            "allCartsInfo": [{
                "complete": False,
            }, {
                "complete": True,
            }]
        }

        #Then transaction_id should exist for complete=True and removed for complete=False
        self.assertEqual(query_result.data, query_expected)


    def test_cart_uuid_should_auto_gen_when_cart_is_set_to_true(self):
        # Given a cart whose transaction_id has not yet been set,

        # when the transaction_id is  set through a mutation,
        class Mutation(CartMutations, graphene.ObjectType):
            pass
        
        schema = graphene.Schema(mutation=Mutation)
        mutation = """
            mutation{
                updateCartCompletion(username: "tester", completion: true){
                    cart{
                        complete
                        transactionId 
                    }
                }
            } 
        """
        result = schema.execute(mutation)

        # the transaction_id should automatically be set.
        self.assertTrue(result.data["updateCartCompletion"]["cart"]["complete"])
        self.assertTrue(result.data["updateCartCompletion"]["cart"]["transactionId"])


    def test_uuid_should_be_removed_from_cart_when_complete_is_false(self):
        # Given a cart with complete=True,

        # when the complete status is set to False through a mutation,
        class Mutation(CartMutations, graphene.ObjectType):
            pass
        
        schema = graphene.Schema(mutation=Mutation)
        mutation = """
             mutation{
                updateCartCompletion(username: "tester2", completion: false){
                    cart{
                        complete
                        transactionId 
                    }
                }
            } 
        """
        result = schema.execute(mutation)

        # then transaction_id should not exist (be removed).
        self.assertFalse(result.data["updateCartCompletion"]["cart"]["complete"])
        self.assertFalse(result.data["updateCartCompletion"]["cart"]["transactionId"])
        

    def test_get_or_create_cart_for_users(self):
        
        # Given a new user whose account just got created,
        new_user = CustomUser.objects.create(
            email = "new_user@email.com",
            username="new_user",
            password="superstrongpassword",
        )

        # when calling getOrCreateAndGetCart mutation 
        class Mutation(CartMutations, AuthMutation, graphene.ObjectType):
            pass

        schema = graphene.Schema(mutation=Mutation)

        mutation = """
            mutation{
                getOrCreateAndGetCart
                {
                    cart{
                        id
                        complete
                    }
                }
            } 
        """
        client = Client(schema)
        executed = client.execute(mutation, context={"user": new_user})

        # a cart, which is also the customer's first cart, should automatically be created for this user.
        self.assertEqual(executed["data"]["getOrCreateAndGetCart"]["cart"]["id"], str(new_user.carts.all().first().pk))
        self.assertFalse(executed["data"]["getOrCreateAndGetCart"]["cart"]["complete"])
 

    def test_should_add_add_item_to_cart_for_authenticated_user(self):

        # Given an authenticated user and a product that the user hasn't yet added,
        product_1: Product = Product.objects.get(image_link="product_1_img_link")
        user_1 = CustomUser.objects.get(username="tester")

        # when the user adds the product,
        class Mutation(CartMutations, graphene.ObjectType):
            pass

        schema = graphene.Schema(mutation=Mutation)
        mutation = """
            mutation addOrRemoveCartItem($operation: String!, $productId: Int!){
            addOrRemoveCartItem(operation: $operation, productId: $productId){
                productsInCart{
                id
                cart{
                    id
                }
                }
            }
            }
        """
        client = Client(schema)
        variables = { "operation": "add", "productId": product_1.pk }

        # the product should now be in the user's cart.
        result = client.execute(mutation, variables=variables, context={"user": user_1})
        returned_products = result["data"]["addOrRemoveCartItem"]["productsInCart"]
        self.assertEqual(returned_products[0]["id"], str(product_1.pk))
        self.assertEqual(returned_products[0]["cart"]["id"], str(user_1.carts.all().first().pk))
        

    def test_should_remove_item_from_cart_for_authenticated_user(self):

        # Given an authenticated user whose cart only has one product.
        product_1: Product = Product.objects.get(image_link="product_1_img_link")
        user_1: CustomUser = CustomUser.objects.get(username="tester")
        user_1_cart = user_1.carts.all().first()
        user_1_cart.items_in_cart.add(product_1)

        # when the user removes the product through the addOrRemoveCartItem mutation,
        class Mutation(CartMutations, graphene.ObjectType):
            pass

        schema = graphene.Schema(mutation=Mutation)
        mutation = """
            mutation addOrRemoveCartItem($operation: String!, $productId: Int!){
            addOrRemoveCartItem(operation: $operation, productId: $productId){
                productsInCart{
                id
                cart{
                    id
                }
                }
            }
            }
        """
        client = Client(schema)
        variables = { "operation": "remove", "productId": product_1.pk }

        # the product should now removed from the user's cart and the cart should now be empty.
        result = client.execute(mutation, variables=variables, context={"user": user_1})
        returned_products = result["data"]["addOrRemoveCartItem"]["productsInCart"]
        self.assertEqual(len(returned_products), 0)


class TestPurchase(GraphQLTestCase):

    maxDiff=None

    def setUp(self):
        composer = Composer.objects.create(
            name="Jeff"
        )

        piece_1 = Composition.objects.create(
            name="Jeff's Song 1",
        )
        piece_1.composers.add(composer)
        piece_2 = Composition.objects.create(
            name="Jeff's Song 2"
        )
        piece_2.composers.add(composer)

        DataAfterPurchase.objects.create(
            midi_link="purchase_data1_midi_link",
            wav_link="purchase_data1_wav_link",
            flac_link="purchase_data1_flac_link",
            pdf_link="purchase_data1_pdf_link",
            composition=piece_1
        )
        DataAfterPurchase.objects.create(
            midi_link="purchase_data2_midi_link",
            wav_link="purchase_data2_wav_link",
            flac_link="purchase_data2_flac_link",
            pdf_link="purchase_data2_pdf_link",
            composition=piece_2
        )

        Product.objects.create(
            price_usd=10,
            image_link="product_1_image_link",
            composition=piece_1,
        )
        Product.objects.create(
            price_usd=10,
            image_link="product_2_image_link",
            composition=piece_2,
        )


    def test_should_attach_data_to_user_after_checkout(self):

        # Given a user who has a few items in their cart and ready to checkout,
        user = CustomUser.objects.create(
            email= "tester@tester.com",
            username= "tester",
            password="strongpassword",
        )
        
        product_1 = Product.objects.get(image_link="product_1_image_link")
        product_2 = Product.objects.get(image_link="product_2_image_link")

        user_cart = Cart.objects.create(customer=user, complete=False, transaction_id=None)
        user_cart.items_in_cart.add(product_1, product_2)

        # when the user clicks pay and paypal has successfully processed the user's payment,
        class Mutation(CartMutations, graphene.ObjectType):
            pass

        schema = graphene.Schema(mutation=Mutation)
        mutation = """
            mutation{
            addDataAfterPurchaseToUserAfterCheckout{
                purchaseSuccess
            }
            }
        """
        client = Client(schema)

        # then the data should now be attached to this user and this user should be able to access it anytime.
        self.assertEqual(len(user.purchased_items.all()), 0)

        result = client.execute(mutation, context={"user": user})

        self.assertTrue(result["data"]["addDataAfterPurchaseToUserAfterCheckout"]["purchaseSuccess"])
        self.assertEqual(user.purchased_items.all().first().composition.name, "Jeff's Song 1" or "Jeff's Song 2")
        self.assertEqual(len(user.purchased_items.all()), 2)


    def test_nothing_should_change_if_purchase_same_product_twice(self):

        # Given a user who already owns 1 product
        user = CustomUser.objects.create(
            email="tester2@tester.com",
            username="tester2",
            password="strongpassword"
        )
        Cart.objects.create(customer=user, complete=False, transaction_id=None)
        data_1 = DataAfterPurchase.objects.get(midi_link="purchase_data1_midi_link")
        data_1.purchased_by.add(user)
        self.assertEqual(1, len(user.purchased_items.all()))

        # when the user, somehow, buys the same thing again
        class Mutation(CartMutations, graphene.ObjectType):
            pass

        schema = graphene.Schema(mutation=Mutation)
        mutation = """
            mutation{
            addDataAfterPurchaseToUserAfterCheckout{
                purchaseSuccess
            }
            }
        """
        client = Client(schema)

        # then nothing should happens, everything should still be the same.
        result = client.execute(mutation, context={"user": user})
        self.assertTrue(result["data"]["addDataAfterPurchaseToUserAfterCheckout"]["purchaseSuccess"])
        self.assertEqual(1, len(user.purchased_items.all()))


        