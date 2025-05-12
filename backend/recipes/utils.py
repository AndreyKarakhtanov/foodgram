from django.conf import settings


def decode_to_integer(string, base=settings.SHORT_URL_BASE):
    """Декодирование закодированной строки в положительное число."""
    integer = 0
    idx = 0
    for char in string:
        power = (len(string) - (idx + 1))
        integer += base.index(char) * (len(base) ** power)
        idx += 1
    return integer
