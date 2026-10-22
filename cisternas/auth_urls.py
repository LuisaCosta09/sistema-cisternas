from django.urls import path
from .auth_views import entrar, sair
urlpatterns = [
path("entrar/", entrar, name="entrar"),
path("sair/", sair, name="sair"),
]