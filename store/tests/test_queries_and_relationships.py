import json

import graphene
from django.test import TestCase
from ecommerce.graphene_queries.queries import (ComposersQuery,
                                                CompositionsQuery, 
                                                DataAfterPurchaseQuery)
from store.models import Composer, Composition, DataAfterPurchase

"""
example cases: https://github.com/graphql-python/graphene-django/blob/master/graphene_django/tests/test_query.
"""


"""
    Test correct query by testing against one of the provided values.
    Test relationship (foreignKey, manytomany) by testing one of the shared values against each other.

    Product model is tested in a separate file in which pagination is also tested.
"""
class TestComposerQueries(TestCase):

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


    def test_composer_query(self):

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
        
        




