from utils.get_user import get_user_from_context
import graphene
from store.models import Composer, Composition, Product, DataAfterPurchase
from ..graphene_types.model_based_types import ComposerType, CompositionType, DataAfterPurchaseType, ProductType
from ..graphene_types.custom_types import AllProductsDataType
from django.core.paginator import Paginator
from math import ceil
from django.db.models import Q


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

    products_purchased_by_current_user = graphene.List(DataAfterPurchaseType, required=True)

    def resolve_all_products_info(root, _, search, limit, page):
        limit = limit if limit and limit >= 0 else 9 if limit >= 0 else 9999
        page = max(page, 1) if page else 1

        all_products = Product.objects.select_related("composition").all().order_by("composition__name")
        filtered_products = all_products.filter(
                                Q(composition__name__unaccent__icontains=search) |
                                Q(composition__composers__name__unaccent__icontains=search) | 
                                #search also in the file extension, some users might look up for "wav", "flac", etc
                                Q(composition__links__midi_link__icontains=search) | 
                                Q(composition__links__flac_link__icontains=search) | 
                                Q(composition__links__pdf_link__icontains=search) | 
                                Q(composition__links__wav_link__icontains=search) 
                            ).distinct() if search else all_products
        paginator = Paginator(filtered_products, limit)
        paginated_products = paginator.page(page)
        return_info = {
            "products": paginated_products.object_list,
            "is_first": not paginated_products.has_previous(),
            "is_last": not paginated_products.has_next(),
            "page_position": {
                "page": page,
                "of": ceil(paginator.count / limit)
            }
        }
        return return_info

    def resolve_products_purchased_by_current_user(unused_root, info):
        del unused_root

        user = get_user_from_context(info)

        try: 
            if  user.is_authenticated:
                product_data = user.purchased_items.all()
                return product_data
            else:
                return []
        except:
            return []

