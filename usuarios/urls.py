from django.urls import path

from . import views

urlpatterns = [
    path("entrar/", views.entrar, name="entrar"),
    path("sair/", views.sair, name="sair"),
    path("usuarios/", views.usuario_listar, name="usuario_listar"),
    path("usuarios/novo/", views.usuario_criar, name="usuario_criar"),
    path("usuarios/<int:pk>/", views.usuario_detalhar, name="usuario_detalhar"),
    path(
        "usuarios/<int:pk>/editar/",
        views.usuario_editar,
        name="usuario_editar",
    ),
    path(
        "usuarios/<int:pk>/excluir/",
        views.usuario_excluir,
        name="usuario_excluir",
    ),
]