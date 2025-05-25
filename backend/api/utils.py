import io

from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def encode_to_string(integer, base=settings.SHORT_URL_BASE):
    """Кодировка положительного числа в строку."""
    if integer == 0:
        return base[0]
    length = len(base)
    string = ''
    while integer != 0:
        index = integer % length
        string = base[index] + string
        integer //= length
    return string


def to_pdf(shopping_cart_list):
    """Создание pdf документа со списком игредиентов."""
    buffer = io.BytesIO()
    width, height = A4
    u_i, d_i, l_i, r_i = height - 2 * cm, 2 * cm, 3 * cm, width - 1 * cm
    width_center = width // 2
    pdf_file = canvas.Canvas(buffer)
    pdf_file.setEncrypt = 'utf-8'
    pdfmetrics.registerFont(
        TTFont('DejaVuSerif', 'DejaVuSerif.ttf', 'UTF-8')
    )
    title_size = 16
    pdf_file.setFont('DejaVuSerif', title_size)
    label = 'Список покупок'
    pdf_file.drawString(
        width_center - (len(label) * title_size) // 4, u_i, label
    )
    size = 14
    count = title_size * 2
    pdf_file.setFont('DejaVuSerif', size)
    for ingredient in shopping_cart_list:
        string = (f'{ingredient["name"]} ({ingredient["measurement_unit"]}) - '
                  f'{ingredient["total_amount"]}')
        if len(string) * size > r_i - l_i:
            string = (f'({ingredient["total_amount"]}) '
                      f'{ingredient["measurement_unit"]} '
                      f'- {ingredient["name"]}')
        pdf_file.drawString(
            l_i, u_i - count, string
        )
        if count + size * 2 > u_i - d_i:
            pdf_file.showPage()
            pdf_file.setFont('DejaVuSerif', size)
            count = 0
        else:
            count += size * 2
    pdf_file.showPage()
    pdf_file.save()
    buffer.seek(0)
    return buffer
