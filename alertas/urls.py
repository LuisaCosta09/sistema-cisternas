from django.urls import path

from . import views

urlpatterns = [
    path(
        "alertas/",
        views.alerta_listar,
        name="alerta_listar",
    ),
    path(
        "alertas/novo/",
        views.alerta_criar,
        name="alerta_criar",
    ),
    path(
        "alertas/<int:pk>/",
        views.alerta_detalhar,
        name="alerta_detalhar",
    ),
    path(
        "alertas/<int:pk>/editar/",
        views.alerta_editar,
        name="alerta_editar",
    ),
    path(
        "alertas/<int:pk>/excluir/",
        views.alerta_excluir,
        name="alerta_excluir",
    ),
]