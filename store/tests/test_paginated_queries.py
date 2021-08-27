from json import dumps

import graphene
from django.test import TestCase
from ecommerce.graphene_queries.store_queries import ProductsQuery
from graphene.test import Client
from graphene_django.utils.testing import GraphQLTestCase
from store.models import  Composition, DataAfterPurchase, Product
from users.models import CustomUser


class TestAllProductsPaginatedQueries(TestCase):

    maxDiff = None

    def test_product_paginated_query(self):

        class Query(ProductsQuery, graphene.ObjectType):
            pass
        
        schema = graphene.Schema(query=Query)

        # For pagination test
        for i in range(20):
            composition = Composition.objects.create(
                name=f"{i}-whatever"
            )
            Product.objects.create(
                price_usd=10,
                image_link=f"{i}_image_link",
                composition=composition
            )

        get_first_three = """
            query{
                allProductsInfo(search: "", page: 1, limit: 3)
                {
                    products{
                        priceUsd
                    }
                    isFirst
                    isLast
                    pagePosition
                    {
                        page
                        of
                    }
                }
            } 
        """

        get_second_five = """
            query{
                allProductsInfo(search: "", page: 2, limit: 5)
                {
                    products{
                        priceUsd
                    }
                    isFirst
                    isLast
                    pagePosition
                    {
                        page
                        of
                    }
                }
            } 
        """

        get_all = """
            query
            {
                allProductsInfo(search: "", page: 1, limit: -1)
                {
                    isLast
                    isFirst
                    pagePosition {
                        page
                        of
                    }
                }
            }

        """

        all_expected = {
                "allProductsInfo": {
                    "isFirst": True,
                    "isLast": True,
                    "pagePosition": {
                        "of": 1,
                        "page": 1
                    }
                }
            } 
        
        all_result = schema.execute(get_all)
        self.assertEqual(all_result.data, all_expected)
        first_three_result = schema.execute(get_first_three)
        self.assertEqual(len(first_three_result.data["allProductsInfo"]["products"]), 3)
        self.assertEqual(first_three_result.data["allProductsInfo"]["pagePosition"], {"of": 7, "page": 1})
        self.assertEqual(first_three_result.data["allProductsInfo"]["isFirst"], True)
        self.assertEqual(first_three_result.data["allProductsInfo"]["isLast"], False)
        second_five_result = schema.execute(get_second_five)
        self.assertEqual(len(second_five_result.data["allProductsInfo"]["products"]), 5)
        self.assertEqual(second_five_result.data["allProductsInfo"]["pagePosition"], {"of": 4, "page": 2})
        self.assertEqual(second_five_result.data["allProductsInfo"]["isFirst"], False)
        self.assertEqual(second_five_result.data["allProductsInfo"]["isLast"], False)


        

class TestPurchasedDataPaginatedQueries(GraphQLTestCase):

    maxDiff = None

    def setUp(self):
        # Given a user who has 11 products,
        user = CustomUser.objects.create(
            username="user_1",
            email="user@user.com",
            password="superstrongpassword",
        )
        for i in range(11):
            composition = Composition.objects.create(
                name=f"{i + 1}-whatever"
            )
            data_after_purchased = DataAfterPurchase.objects.create(
                composition=composition
            )
            user.purchased_items.add(data_after_purchased)


    def test_when_query_the_first_page(self):
        user = CustomUser.objects.get(username="user_1")
        
        class Query(ProductsQuery, graphene.ObjectType):
            pass
        schema = graphene.Schema(query=Query)
        query = """
             query {
                productsPurchasedByCurrentUser(page: 1, limit: 5, search: ""){
                    isFirst
                    isLast
                    data{
                        composition{
                            name
                        }
                    }
                    pagePosition{
                        page
                        of
                    }
                }
             }
        """
        client = Client(schema)
        executed = client.execute(query, context={"user": user})
        result = executed["data"]["productsPurchasedByCurrentUser"]

        # then data should be like this
        self.assertEqual(len(result["data"]), 5)
        self.assertEqual(result["isFirst"], True)
        self.assertEqual(result["isLast"], False)
        self.assertEqual(result["pagePosition"]["page"], 1)
        self.assertEqual(result["pagePosition"]["of"], 3)
        

    def test_when_query_the_second_page(self):
        user = CustomUser.objects.get(username="user_1")
        
        class Query(ProductsQuery, graphene.ObjectType):
            pass
        schema = graphene.Schema(query=Query)
        query = """
             query {
                productsPurchasedByCurrentUser(page: 2, limit: 5, search: ""){
                    isFirst
                    isLast
                    data{
                        composition{
                            name
                        }
                    }
                    pagePosition{
                        page
                        of
                    }
                }
             }
        """
        client = Client(schema)
        executed = client.execute(query, context={"user": user})
        result = executed["data"]["productsPurchasedByCurrentUser"]

        # then data should be like this
        self.assertEqual(len(result["data"]), 5)
        self.assertEqual(result["isFirst"], False)
        self.assertEqual(result["isLast"], False)
        self.assertEqual(result["pagePosition"]["page"], 2)
        self.assertEqual(result["pagePosition"]["of"], 3)

    def test_when_query_the_last_page(self):
        user = CustomUser.objects.get(username="user_1")
        
        class Query(ProductsQuery, graphene.ObjectType):
            pass
        schema = graphene.Schema(query=Query)
        query = """
             query {
                productsPurchasedByCurrentUser(page: 3, limit: 5, search: ""){
                    isFirst
                    isLast
                    data{
                        composition{
                            name
                        }
                    }
                    pagePosition{
                        page
                        of
                    }
                }
             }
        """
        client = Client(schema)
        executed = client.execute(query, context={"user": user})
        result = executed["data"]["productsPurchasedByCurrentUser"]

        # then data should be like this
        self.assertEqual(len(result["data"]), 1)
        self.assertEqual(result["isFirst"], False)
        self.assertEqual(result["isLast"], True)
        self.assertEqual(result["pagePosition"]["page"], 3)
        self.assertEqual(result["pagePosition"]["of"], 3)
