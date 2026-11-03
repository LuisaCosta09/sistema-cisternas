from django.urls import path

from . import views

urlpatterns = [
    path(
        "cisternas/",
        views.cisterna_listar,
        name="cisterna_listar",
    ),
    path(
        "cisternas/nova/",
        views.cisterna_criar,
        name="cisterna_criar",
    ),
    path(
        "cisternas/<int:pk>/",
        views.cisterna_detalhar,
        name="cisterna_detalhar",
    ),
    path(
        "cisternas/<int:pk>/editar/",
        views.cisterna_editar,
        name="cisterna_editar",
    ),
    path(
        "cisternas/<int:pk>/excluir/",
        views.cisterna_excluir,
        name="cisterna_excluir",
    ),
]
