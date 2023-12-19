from rest_framework.pagination import PageNumberPagination


class PageNumberLimitPaginator(PageNumberPagination):
    page_size_query_param = 'limit'
