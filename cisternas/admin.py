from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import (
    Usuario,
    Cisterna,
    Monitoramento,
    Alerta,
    Abastecimento,
)


class UsuarioAdminCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("username", "nome", "cpf", "email")


class UsuarioAdminChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Usuario
        fields = "__all__"


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    add_form = UsuarioAdminCreationForm
    form = UsuarioAdminChangeForm
    readonly_fields = ("last_login", "date_joined")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Informações pessoais", {"fields": ("nome", "cpf", "email")}),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Datas importantes", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "nome",
                    "cpf",
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    list_display = ("username", "nome", "cpf")
    search_fields = ("nome", "cpf", "username", "email")


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