from django.contrib import admin

from .models import (
    Usuario,
    Cisterna,
    Monitoramento,
    Alerta,
    Abastecimento,
)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "nome", "cpf")
    search_fields = ("nome", "cpf", "user__username", "user__email")


@admin.register(Cisterna)
class CisternaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "usuario",
        "latitude",
        "longitude",
        "capacidade",
        "status",
    )
    list_filter = ("status",)
    search_fields = ("latitude", "longitude", "descricao")


@admin.register(Monitoramento)
class MonitoramentoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "usuario",
        "cisterna",
        "dataHora",
        "nivelAgua",
        "consumo",
        "situacao",
    )
    list_filter = ("situacao", "dataHora")



@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cisterna",
        "tipo",
        "status",
        "dataHora",
    )
    list_filter = ("tipo", "status", "dataHora")
    search_fields = ("tipo", "mensagem")


@admin.register(Abastecimento)
class AbastecimentoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "usuario",
        "cisterna",
        "dataHora",
        "quantidadeAgua",
        "tipo",
        "status",
    )
    list_filter = ("tipo", "status", "dataHora")
    search_fields = ("tipo", "observacao")