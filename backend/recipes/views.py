from django.shortcuts import redirect

from .utils import decode_to_integer


def short_link(request, slug):
    """Редирект по короткой ссылке на страницу рецепта."""
    return redirect(
        f'/recipes/{decode_to_integer(slug)}/'
    )
