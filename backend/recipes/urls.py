from django.urls import path

from . import views

urlpatterns = [
    path('s/<slug:slug>', views.short_link, name='shorten'),
]
