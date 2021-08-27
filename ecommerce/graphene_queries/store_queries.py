from utils.paginate import paginate
from utils.search_through_composition import search_through_composition
from utils.check_and_get_pagination_values import check_and_get_pagination_values
from utils.get_user import get_user_from_context
import graphene
from store.models import Composer, Composition, Product, DataAfterPurchase
from ..graphene_types.model_based_types import ComposerType, CompositionType, DataAfterPurchaseType, ProductType
from ..graphene_types.custom_types import AllProductsDataType, AllPurchasedDataType


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

    products_purchased_by_current_user = graphene.Field(AllPurchasedDataType, 
                        search=graphene.String(required=False), limit=graphene.Int(required=False), 
                        page=graphene.Int(required=False))


    def resolve_all_products_info(root, _, search, limit, page):
        limit, page = check_and_get_pagination_values(limit, page)

        all_products = Product.objects.select_related("composition").all().order_by("composition__name")

        filtered_products = search_through_composition(all_products, search)

        paginated_products, is_first, is_last, page_position = paginate(
            filtered_products, limit, page
        )
        
        return_info = {
            "products": paginated_products,
            "is_first": is_first,
            "is_last": is_last,
            "page_position": page_position
        }
        return return_info


    def resolve_products_purchased_by_current_user(unused_root, info, search, limit, page):
        del unused_root

        limit, page = check_and_get_pagination_values(limit, page)
        user = get_user_from_context(info)

        try: 
            if  user.is_authenticated:
                all_data = user.purchased_items.all().order_by("composition__name")

                filtered_data = search_through_composition(all_data, search)

                paginated_data, is_first, is_last, page_position = paginate(
                    filtered_data, limit, page
                )

                return_info =  {
                   "data": paginated_data,
                   "is_first": is_first,
                   "is_last": is_last,
                   "page_position": page_position
                }
                return return_info

            else:
                return {}

        except:
            return {}

