from django.urls import path
from . import views
urlpatterns = [

path(
"usuarios/",
views.usuario_listar,
name="usuario_listar",
),
path(
"usuarios/novo/",
views.usuario_criar,
name="usuario_criar",
),
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