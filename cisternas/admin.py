from django.contrib import admin
from .models import Usuario, Cisterna, Monitoramento, Relatorio, Alerta, Abastecimento


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("user__username", "user__email")


@admin.register(Cisterna)
class CisternaAdmin(admin.ModelAdmin):
    list_display = ("id", "localizacao", "capacidade", "status", "usuario")
    list_filter = ("status",)
    search_fields = ("localizacao", "descricao")


@admin.register(Monitoramento)
class MonitoramentoAdmin(admin.ModelAdmin):
    list_display = ("id", "cisterna", "dataHora", "nivelAgua", "consumo", "situacao")
    list_filter = ("situacao", "dataHora")


@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "usuario",
        "cisterna",
        "periodoInicio",
        "periodoFim",
        "formato",
        "dataGeracao",
    )
    list_filter = ("formato", "dataGeracao")


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ("id", "cisterna", "tipo", "status", "dataHora")
    list_filter = ("tipo", "status")


@admin.register(Abastecimento)
class AbastecimentoAdmin(admin.ModelAdmin):
    list_display = ("id", "cisterna", "dataHora", "quantidadeAgua", "tipo", "status")
    list_filter = ("tipo", "status")