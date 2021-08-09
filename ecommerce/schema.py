#root type
#DjangoObjectType automatically generate types. We'll just have to expose them as fields now
#this is like urls.py
import graphene
from django.contrib.postgres.search import  SearchVector
from graphene.types.scalars import Boolean
from graphene_django import DjangoObjectType
from graphql_auth import mutations
from graphql_auth.schema import MeQuery, UserQuery
from django.core.paginator import Paginator
from store.models import Composer, Composition, DataAfterPurchase, Product

class ProductType(DjangoObjectType):
    class Meta: 
        model = Product
        fields = "__all__"

class CompositionType(DjangoObjectType):
    class Meta: 
        model = Composition
        fields = "__all__"

class ComposerType(DjangoObjectType):
    class Meta: 
        model = Composer
        fields = "__all__"

class DataAfterPurchaseType(DjangoObjectType):
    class Meta: 
        model = DataAfterPurchase
        fields = "__all__"

class PagePositionType(graphene.ObjectType):
    page = graphene.Int()
    of = graphene.Int()

class AllProductsDataType(graphene.ObjectType):
    products = graphene.List(ProductType)
    is_first = graphene.Boolean()
    is_last = graphene.Boolean()
    page_position = graphene.Field(PagePositionType)

class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    token_auth = mutations.ObtainJSONWebToken.Field()
    update_account = mutations.UpdateAccount.Field()
    refresh_token = mutations.RefreshToken.Field()

class ComposerQuery(graphene.ObjectType):
    all_composers_info = graphene.List(ComposerType)

    def resolve_all_composers(root, info):
        all_composers = Composer.objects.prefetch_related("compositions").all()
        return all_composers

class CompositionQuery(graphene.ObjectType):
    all_compositions_info = graphene.List(CompositionType)

    def resolve_all_compositions(root, info):
        all_compositions = Composition.objects.prefetch_related("composers").all() 
        return all_compositions

class ProductsQuery(graphene.ObjectType):
    all_products_info = graphene.Field(AllProductsDataType, search=graphene.String(required=False), 
                        limit=graphene.Int(required=False), page=graphene.Int(required=False))

    def resolve_all_products_info(root, _, search, limit, page):
        limit = limit if limit else 9
        page = max(page, 1) if page else 1

        all_products = Product.objects.select_related("composition").all().order_by("composition__name")
        filtered_products = all_products.annotate(
                            search=SearchVector("composition__name", "composition__composers__name", config="unaccent")
                            ).filter(search__icontains=search) if search else all_products
        paginator = Paginator(filtered_products, limit)
        paginated_products = paginator.page(page)
        return_info = {
            "products": paginated_products.object_list,
            # Do not check against page number as page nums 
            # are dynamic and can change (eg. starting at page 0).
            "is_first": not paginated_products.has_previous(),
            "is_last": not paginated_products.has_next(),
            "page_position": {
                "page": page,
                "of": paginator.count
            }
        }
        return return_info

class Query(UserQuery, MeQuery, ComposerQuery, ProductsQuery, CompositionQuery, graphene.ObjectType):
   
    all_data_after_purchase_only = graphene.List(DataAfterPurchaseType)
    product_by_name = graphene.Field(ProductType, name=graphene.String(required=True))
    def resolve_product_by_name(root, _, name):
        try:
            return Product.objects.get(name=name)
        except Product.DoesNotExist:
            return None
    
    #hide this in prod
    def all_data_after_purchase_only(root, _):
        return DataAfterPurchase.objects.all()

class Mutation(AuthMutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)


