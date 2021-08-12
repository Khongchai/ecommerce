import json

import graphene
from django.test import TestCase
from ecommerce.graphene_queries.store_queries import (ComposersQuery,
                                                CompositionsQuery,
                                                DataAfterPurchaseQuery,
                                                ProductsQuery)
from store.models import Composer, Composition, DataAfterPurchase, Product

"""
example cases: https://github.com/graphql-python/graphene-django/blob/master/graphene_django/tests/test_query.
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
            free=True
        )
        Product.objects.create(
            price_usd=20,
            image_link="product_2_image_link",
            composition=piece_2,
            free=False
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
                    "compositions": [
                        {
                            "name": "Eine Kleine Nacht Musik"
                        }
                    ],
                    "name": "Wolfgang Amadeus Mozart"        
                },
                {
                    "compositions": [
                        {
                            "name": "Moonlight Sonata"       
                        }
                    ],
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
                    "links": [
                        {
                            "midiLink": "purchase_data1_midi_link"
                        }
                    ],
                    "name": "Eine Kleine Nacht Musik"
                },
                {
                    "links": [
                        {
                            "midiLink": "purchase_data2_midi_link"
                        }
                    ],
                    "name": "Moonlight Sonata"
                }
            ]
        }
        self.assertEqual(data_after_purchase_result.data, data_after_purchase_expected)
        self.assertEqual(compositions_result.data, compositions_expected)
        
        
class TestPaginatedQueries(TestCase):

    maxDiff = None

    def test_product_paginated_query(self):

        class Query(ProductsQuery, graphene.ObjectType):
            pass
        
        schema = graphene.Schema(query=Query)

        # For pagination test
        for i in range(20):
            Product.objects.create(
                price_usd=10,
                image_link=f"{i}_image_link",
                free=True
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

    def test_product_searched_paginated_query(self):

        claude = Composer.objects.create(name="Achille-Claude Debussy")
        claude2 = Composer.objects.create(name="Achille-Claude Debussy2")
        pyotr = Composer.objects.create(name="Pyotr Ilyich Tchaikovsky")
        jules = Composer.objects.create(name="Jules Émile Frédéric Massenet")
        traditional = Composer.objects.create(name="Traditional")

        moon = Composition.objects.create(name="A Song to the Moon")
        lake = Composition.objects.create(name="Swan Lake")
        meditation = Composition.objects.create(name="Meditation")
        arm = Composition.objects.create(name="Pierre's Right Arm")
        moon.composers.add(claude)
        moon.composers.add(claude2)
        lake.composers.add(pyotr)
        meditation.composers.add(jules)
        arm.composers.add(traditional)

        Product.objects.create(
            price_usd=10,
            image_link=f"{moon}-link",
            composition=moon,
            free=False,
        )
        Product.objects.create(
            price_usd=10,
            image_link=f"{lake}-link",
            composition=lake,
            free=False,
        )
        Product.objects.create(
            price_usd=10,
            image_link=f"{meditation}-link",
            composition=meditation,
            free=False,
        )
        Product.objects.create(
            price_usd=10,
            image_link=f"{arm}-link",
            composition=arm,
            free=False,
        )

        class Query(ProductsQuery, graphene.ObjectType):
            pass
        
        schema = graphene.Schema(query=Query)
        
        debussy_and_massenet = """
             query{
                allProductsInfo(search: "ss", limit: -1, page: 1)
                {
                    products{
                    composition{
                        composers{
                        name
                        }
                    }
                    }
                }
                }
        """

        debussy_and_massenet_result = schema.execute(debussy_and_massenet)
        self.assertEqual(debussy_and_massenet_result.data["allProductsInfo"]["products"][0]
                        ["composition"]["composers"][0]["name"], "Achille-Claude Debussy")
        self.assertEqual(debussy_and_massenet_result.data["allProductsInfo"]["products"][0]
                        ["composition"]["composers"][1]["name"], "Achille-Claude Debussy2")
        self.assertEqual(debussy_and_massenet_result.data["allProductsInfo"]["products"][1]
                        ["composition"]["composers"][0]["name"], "Jules Émile Frédéric Massenet")
        
        


