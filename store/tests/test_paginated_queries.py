from users.models import CustomUser
from store.models import Composer, Composition, DataAfterPurchase, Product
import graphene
from ecommerce.graphene_queries.store_queries import ProductsQuery
from django.test import TestCase
from graphene_django.utils.testing import GraphQLTestCase


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

        DataAfterPurchase.objects.create(
            wav_link="lake.wav",
            composition=lake,
        )
        DataAfterPurchase.objects.create(
            pdf_link="moon.pdf",
            composition=moon,
        )

        Product.objects.create(
            price_usd=10,
            image_link=f"{moon}-link",
            composition=moon,
        )
        Product.objects.create(
            price_usd=10,
            image_link=f"{lake}-link",
            composition=lake,
        )
        Product.objects.create(
            price_usd=10,
            image_link=f"{meditation}-link",
            composition=meditation,
        )
        Product.objects.create(
            price_usd=10,
            image_link=f"{arm}-link",
            composition=arm,
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

        swan_lake = """
            query{
                allProductsInfo(search: "wav", limit: -1, page: 1)
                {
                    products{
                        composition{
                            name
                        }
                    }
                }
            } 
        """

        song_to_the_moon = """
            query{
                allProductsInfo(search: "pdf", limit: -1, page: 1)
                {
                    products{
                        composition{
                            name
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

        swan_lake_result = schema.execute(swan_lake)
        self.assertEqual(swan_lake_result.data["allProductsInfo"]["products"][0]
                        ["composition"]["name"], "Swan Lake")
        
        song_to_the_moon_result = schema.execute(song_to_the_moon)
        self.assertEqual(song_to_the_moon_result.data["allProductsInfo"]["products"][0]
                        ["composition"]["name"], "A Song to the Moon")
        

class TestPurchasedDataPaginatedQueries(GraphQLTestCase):

    maxDiff = None

    def setUp(self):
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


    def test_purchased_data_paginated_query_first_page(self):
        # query = """
        #      query {
        #         productsPurchasedByCurrentUser(page: 1){
        #             isFirst
        #             isLast
        #             data{
                        
        #             }
        #         }
        #      }
        # """
        pass

    def test_purchased_data_paginated_query_second_page(self):
        pass

    def test_purchased_data_paginated_query_last_page(self):
        pass