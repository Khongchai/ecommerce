def check_and_get_pagination_values(limit, page):
    limit = limit if limit and limit >= 0 else 9 if limit >= 0 else 9999
    page = max(page, 1) if page else 1

    return (
        limit, page
    ) 