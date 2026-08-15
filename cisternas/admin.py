from django.contrib import admin
from .models import (
    Usuario,
    Cisterna,
    Monitoramento,
    Relatorio,
    Alerta,
    Abastecimento,
)

admin.site.register(Usuario)
admin.site.register(Cisterna)
admin.site.register(Monitoramento)
admin.site.register(Relatorio)
admin.site.register(Alerta)
admin.site.register(Abastecimento)