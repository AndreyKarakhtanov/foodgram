from foodgram_backend import settings
from rest_framework.pagination import PageNumberPagination


class LimitPagination(PageNumberPagination):
    """Пагинация с page и limit."""
    page_size = settings.PAGE_SIZE
    page_size_query_param = 'limit'
