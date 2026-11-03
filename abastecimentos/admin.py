from django.contrib import admin

from .models import Abastecimento


@admin.register(Abastecimento)
class AbastecimentoAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "cisterna",
        "dataHora",
        "quantidadeAgua",
        "tipo",
        "status",
    )
    list_filter = ("tipo", "status", "dataHora")
    search_fields = ("tipo", "observacao")