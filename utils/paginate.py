from django.core.paginator import Paginator
from math import ceil

def paginate(obj_list, limit, page):
    paginator = Paginator(obj_list, limit)
    paginated_data = paginator.page(page)

    return (
        paginated_data.object_list,
        not paginated_data.has_previous(),
        not paginated_data.has_next(),
        {
            "page": page,
            "of": ceil(paginator.count / limit) 
        }
    )