import json

import graphene
from django.test import TestCase
from graphene.test import Client
from ecommerce.graphene_queries.store_queries import (ComposersQuery,
                                                      CompositionsQuery,
                                                      DataAfterPurchaseQuery,
                                                      ProductsQuery)
from graphene_django.utils.testing import GraphQLTestCase
from store.models import Composer, Composition, DataAfterPurchase, Product, CustomUser

"""
example cases: https://github.com/graphql-python/graphene-django/blob/master/graphene_django/tests/test_query.py
"""

class TestQueries(TestCase):

    maxDiff = None

    def setUp(self):
        composer_name_1 = "Wolfgang Amadeus Mozart"
        composer_name_2 = "Ludwig van Beethoven"
        composer_1 = Composer.objects.create(name=composer_name_1)
        composer_2 = Composer.objects.create(name=composer_name_2)

        piece_1: Composition = Composition.objects.create(name="Eine Kleine Nacht Musik")
        piece_1.composers.add(composer_1)
        piece_2 = Composition.objects.create(name="Moonlight Sonata")
        piece_2.composers.add(composer_2)

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

        # get a lot of these for pagination testing
        Product.objects.create(
            price_usd=10,
            image_link="product_1_image_link",
            composition=piece_1,
        )
        Product.objects.create(
            price_usd=20,
            image_link="product_2_image_link",
            composition=piece_2,
        )


    def test_composer_query(self):
        """
            Simple fetching of Composer objects 
        """

        class Query(ComposersQuery, graphene.ObjectType):
            pass

        schema = graphene.Schema(query=Query)
        query = """
            query{
                allComposersInfo{
                    name
                }
            }
        """
        result = schema.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(result.data["allComposersInfo"][0]["name"], "Wolfgang Amadeus Mozart")
        self.assertEqual(result.data["allComposersInfo"][1]["name"], "Ludwig van Beethoven")


    def test_composition_query(self):
        """
            Simple fetching of Composition objects
        """

        class Query(CompositionsQuery, graphene.ObjectType):
            pass

        schema = graphene.Schema(query=Query)
        query = """
            query{
                allCompositionsInfo{
                    name
                }
            }
        """
        result = schema.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(result.data["allCompositionsInfo"][0]["name"], "Eine Kleine Nacht Musik")
        self.assertEqual(result.data["allCompositionsInfo"][1]["name"], "Moonlight Sonata")


    def test_purchase_data_query(self):
        """
            Simple fetching of DataAfterPurchase object
        """

        class Query(DataAfterPurchaseQuery, graphene.ObjectType):
            pass

        schema = graphene.Schema(query=Query)
        query = """
            query{
                allDataAfterPurchase{
                    midiLink
                }
            } 
        """
        result = schema.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(result.data["allDataAfterPurchase"][0]["midiLink"],"purchase_data1_midi_link")
        self.assertEqual(result.data["allDataAfterPurchase"][1]["midiLink"], "purchase_data2_midi_link")

    def test_product_data_relationship_query(self):
        """
            Testing relationship between prodcut and data
        """

        class Query(ProductsQuery, graphene.ObjectType):
            pass
        
        schema = graphene.Schema(query=Query)
        query = """
            query{
                allProductsInfo(search: "", page: 1, limit: -1){
                    products
                    {
                        id
                    }
                }
            } 
        """
        result = schema.execute(query)
        self.assertEqual(len(result.data["allProductsInfo"]["products"]), 2)


    def test_many_to_many_composer_compositions_relationship(self):

        class Query(ComposersQuery, CompositionsQuery, graphene.ObjectType):
           pass

        schema = graphene.Schema(query=Query)
        composers_query = """
            query{
                allComposersInfo{
                    name
                    compositions{
                        name
                    }
                }
            } 
        """
        compositions_query = """
            query {
                allCompositionsInfo{
                    name
                    composers{
                        name
                    }
                }
            }
        """
        composers_result = schema.execute(composers_query)
        compositions_result = schema.execute(compositions_query)
        composers_expected = {
            "allComposersInfo": [
                {
                    "compositions": 
                        [{
                            "name": "Eine Kleine Nacht Musik"
                        }]
                    ,
                    "name": "Wolfgang Amadeus Mozart"        
                },
                {
                    "compositions": 
                        [{
                            "name": "Moonlight Sonata"       
                        }]
                    ,
                    "name": "Ludwig van Beethoven"
                }
            ]
        }
        compositions_expected = {
            "allCompositionsInfo": [
                {
                    "composers": [
                        {
                            "name": "Wolfgang Amadeus Mozart"
                        }
                    ],
                    "name": "Eine Kleine Nacht Musik"
                },
                {
                    "composers": [
                        {
                            "name": "Ludwig van Beethoven"
                        }
                    ],
                    "name": "Moonlight Sonata"
                }
            ]
        }
        self.assertEqual(composers_result.data, composers_expected)
        self.assertEqual(compositions_result.data, compositions_expected)

    def test_many_to_many_compositions_data_after_purchase_relationship(self):

        class Query(DataAfterPurchaseQuery, CompositionsQuery, graphene.ObjectType):
           pass

        schema = graphene.Schema(query=Query)
        data_after_purchase_query= """
            query{
                allDataAfterPurchase{
                    midiLink
                    composition{
                        name
                    }
                }
            }
        """
        compositions_query = """
            query{
                allCompositionsInfo{
                    name
                    links{
                        midiLink
                    }
                }
            }
        """
        data_after_purchase_result = schema.execute(data_after_purchase_query)
        compositions_result = schema.execute(compositions_query)
        data_after_purchase_expected= {
            "allDataAfterPurchase": [
                {
                    "composition": {
                        "name": "Eine Kleine Nacht Musik"
                    },
                    "midiLink": "purchase_data1_midi_link"
                },
                {
                    "composition": {
                        "name": "Moonlight Sonata"
                    },
                    "midiLink": "purchase_data2_midi_link"
                }
            ]
        }
        compositions_expected = {
            "allCompositionsInfo": [
                {
                    "links": 
                        {
                            "midiLink": "purchase_data1_midi_link"
                        }
                    ,
                    "name": "Eine Kleine Nacht Musik"
                },
                {
                    "links": 
                        {
                            "midiLink": "purchase_data2_midi_link"
                        }
                    ,
                    "name": "Moonlight Sonata"
                }
            ]
        }
        self.assertEqual(data_after_purchase_result.data, data_after_purchase_expected)
        self.assertEqual(compositions_result.data, compositions_expected)


class TestPurchasedData(GraphQLTestCase):

    def setup():
        pass

    def test_products_ownership(self):

        # Given an authenticated user who has already purchased something (owns some products),
        composer_name_1 = "Wolfgang Amadeus Mozart"
        composer_name_2 = "Ludwig van Beethoven"
        composer_1 = Composer.objects.create(name=composer_name_1)
        composer_2 = Composer.objects.create(name=composer_name_2)

        piece_1: Composition = Composition.objects.create(name="Eine Kleine Nacht Musik")
        piece_1.composers.add(composer_1)
        piece_2 = Composition.objects.create(name="Moonlight Sonata")
        piece_2.composers.add(composer_2)

        data_1 = DataAfterPurchase.objects.create(
            midi_link="purchase_data1_midi_link",
            wav_link="purchase_data1_wav_link",
            flac_link="purchase_data1_flac_link",
            pdf_link="purchase_data1_pdf_link",
            youtube_link="purchase_data1_youtube_link",
            composition=piece_1
        )
        data_2 = DataAfterPurchase.objects.create(
            midi_link="purchase_data2_midi_link",
            wav_link="purchase_data2_wav_link",
            flac_link="purchase_data2_flac_link",
            pdf_link="purchase_data2_pdf_link",
            youtube_link="purchase_data2_youtube_link",
            composition=piece_2
        )

        Product.objects.create(
            price_usd=10,
            image_link="product_1_image_link",
            composition=piece_1,
        )
        Product.objects.create(
            price_usd=20,
            image_link="product_2_image_link",
            composition=piece_2,
        )

        user = CustomUser.objects.create(
            username="user",
            email="user@user.com",
            password="superstrongpassword"
        )

        user.purchased_items.add(data_1, data_2)

        # when user asks to see the products they own

        class Query(ProductsQuery, graphene.ObjectType):
            pass

        schema = graphene.Schema(query=Query)
        query = """
            query{
                productsPurchasedByCurrentUser(page: 1, limit: 2, search: ""){
                    data{
                        midiLink
                        wavLink
                        flacLink
                        pdfLink
                        youtubeLink
                        composition{
                        name
                        }
                    }
                }
                }
        """
        query_expected = {
            "productsPurchasedByCurrentUser": {
                "data": [
                    {
                        "midiLink": "purchase_data1_midi_link",
                        "wavLink": "purchase_data1_wav_link",
                        "flacLink": "purchase_data1_flac_link",
                        "pdfLink": "purchase_data1_pdf_link",
                        "youtubeLink": "purchase_data1_youtube_link",
                        "composition": {
                            "name": "Eine Kleine Nacht Musik"
                        }
                    },
                    {
                        "midiLink": "purchase_data2_midi_link",
                        "wavLink": "purchase_data2_wav_link",
                        "flacLink": "purchase_data2_flac_link",
                        "pdfLink": "purchase_data2_pdf_link",
                        "youtubeLink": "purchase_data2_youtube_link",
                        "composition": {
                            "name": "Moonlight Sonata"
                        }
                    }
                ]
            }
        }

        client = Client(schema)
        
        # then products should be there with all necessary details.
        result = client.execute(query, context={"user": user})
        self.assertEqual(query_expected, result["data"])
