from django.urls import path

from . import views

urlpatterns = [
    path(
        "abastecimentos/",
        views.abastecimento_listar,
        name="abastecimento_listar",
    ),
    path(
        "abastecimentos/novo/",
        views.abastecimento_criar,
        name="abastecimento_criar",
    ),
    path(
        "abastecimentos/<int:pk>/",
        views.abastecimento_detalhar,
        name="abastecimento_detalhar",
    ),
    path(
        "abastecimentos/<int:pk>/editar/",
        views.abastecimento_editar,
        name="abastecimento_editar",
    ),
    path(
        "abastecimentos/<int:pk>/excluir/",
        views.abastecimento_excluir,
        name="abastecimento_excluir",
    ),
]
