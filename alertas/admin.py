from django.contrib import admin

from .models import Alerta


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = (
        "cisterna",
        "tipo",
        "status",
        "dataHora",
    )
    list_filter = ("tipo", "status", "dataHora")
    search_fields = ("tipo", "mensagem")