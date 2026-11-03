from django.urls import path

from . import views

urlpatterns = [
    path("", views.pagina_inicial, name="landing"),
    path("painel/", views.inicio, name="inicio"),
]