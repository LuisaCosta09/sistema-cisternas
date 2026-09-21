from django.urls import path
from . import views
urlpatterns = [
 path(
 "",
 views.inicio,
 name="inicio",
 ),
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
]