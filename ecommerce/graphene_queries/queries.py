import graphene
from store.models import Composer, Composition, Product, DataAfterPurchase
from ..graphene_types.model_based_types import ComposerType, CompositionType, DataAfterPurchaseType
from ..graphene_types.custom_types import AllProductsDataType
from django.contrib.postgres.search import  SearchVector
from django.core.paginator import Paginator
from math import ceil


class ComposersQuery(graphene.ObjectType):
    all_composers_info = graphene.List(ComposerType)

    def resolve_all_composers_info(root, _):
        all_composers = Composer.objects.prefetch_related("compositions").all()
        return all_composers

class CompositionsQuery(graphene.ObjectType):
    all_compositions_info = graphene.List(CompositionType)

    def resolve_all_compositions_info(root, _):
        all_compositions = Composition.objects.prefetch_related("composers").all() 
        return all_compositions

class DataAfterPurchaseQuery(graphene.ObjectType):
    all_data_after_purchase = graphene.List(DataAfterPurchaseType)

    def resolve_all_data_after_purchase(root, _):
        all_data = DataAfterPurchase.objects.select_related("composition").all()
        return all_data

class ProductsQuery(graphene.ObjectType):
    all_products_info = graphene.Field(AllProductsDataType, search=graphene.String(required=False), 
                        limit=graphene.Int(required=False), page=graphene.Int(required=False))

    def resolve_all_products_info(root, _, search, limit, page):
        limit = limit if limit and limit >= 0 else 9 if limit >= 0 else 9999
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
                "of": ceil(paginator.count / limit)
            }
        }
        return return_info
