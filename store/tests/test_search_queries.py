import graphene
from ecommerce.graphene_queries.store_queries import ProductsQuery
from graphene_django.utils.testing import GraphQLTestCase
from store.models import Composer, Composition, DataAfterPurchase, Product


class TestSearchQueries(GraphQLTestCase):

    def setUp(self):
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


    def test_product_searched_query(self):
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
