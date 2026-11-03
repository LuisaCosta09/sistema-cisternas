from django.contrib import admin

from .models import Cisterna


@admin.register(Cisterna)
class CisternaAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "latitude",
        "longitude",
        "capacidade",
        "status",
    )
    list_filter = ("status",)
    search_fields = ("latitude", "longitude", "descricao")