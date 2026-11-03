from django.urls import path

from . import views

urlpatterns = [
    path(
        "monitoramentos/",
        views.monitoramento_listar,
        name="monitoramento_listar",
    ),
    path(
        "monitoramentos/novo/",
        views.monitoramento_criar,
        name="monitoramento_criar",
    ),
    path(
        "monitoramentos/<int:pk>/",
        views.monitoramento_detalhar,
        name="monitoramento_detalhar",
    ),
    path(
        "monitoramentos/<int:pk>/editar/",
        views.monitoramento_editar,
        name="monitoramento_editar",
    ),
    path(
        "monitoramentos/<int:pk>/excluir/",
        views.monitoramento_excluir,
        name="monitoramento_excluir",
    ),
]