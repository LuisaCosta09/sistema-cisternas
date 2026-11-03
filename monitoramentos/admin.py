from django.contrib import admin

from .models import Monitoramento


@admin.register(Monitoramento)
class MonitoramentoAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "cisterna",
        "dataHora",
        "nivelAgua",
        "consumo",
        "situacao",
    )
    list_filter = ("situacao", "dataHora")
