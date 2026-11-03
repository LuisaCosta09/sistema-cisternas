from decimal import Decimal
from django import forms
from cisternas.models import Cisterna
from usuarios.models import Usuario
from .models import Abastecimento

class AbastecimentoForm(forms.ModelForm):

    tipo = forms.ChoiceField(
        label="Tipo de abastecimento",
        choices=[
            ("", "Selecione o tipo de abastecimento"),
            ("Caminhão-pipa", "Caminhão-pipa"),
            ("Captação de chuva", "Captação de chuva"),
            ("Rede pública", "Rede pública"),
            ("Poço", "Poço"),
            ("Outro", "Outro"),
        ],
        help_text="Selecione de onde veio a água.",
        error_messages={
            "required": "Selecione o tipo de abastecimento.",
            "invalid_choice": "Selecione um tipo válido.",
        },
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    status = forms.ChoiceField(
        label="Status",
        choices=[
            ("", "Selecione o status do abastecimento"),
            ("Pendente", "Pendente"),
            ("Em andamento", "Em andamento"),
            ("Concluído", "Concluído"),
            ("Cancelado", "Cancelado"),
        ],
        help_text="Selecione a situação atual do abastecimento.",
        error_messages={
            "required": "Selecione o status do abastecimento.",
            "invalid_choice": "Selecione um status válido.",
        },
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Abastecimento

        fields = (
            "usuario",
            "cisterna",
            "dataHora",
            "quantidadeAgua",
            "tipo",
            "observacao",
            "status",
        )

        labels = {
            "usuario": "Usuário",
            "cisterna": "Cisterna",
            "dataHora": "Data e hora",
            "quantidadeAgua": "Quantidade de água",
            "tipo": "Tipo de abastecimento",
            "observacao": "Observação",
            "status": "Status",
        }

        help_texts = {
            "usuario": "Selecione o usuário relacionado ao abastecimento.",
            "cisterna": "A cisterna deve pertencer ao usuário selecionado.",
            "dataHora": "Informe quando o abastecimento foi realizado.",
            "quantidadeAgua": "Informe uma quantidade maior que zero.",
            "tipo": "Identifique a forma ou o tipo do abastecimento.",
            "observacao": "Registre uma observação curta sobre o abastecimento.",
            "status": "Informe a situação atual do registro.",
        }

        error_messages = {
            "usuario": {
                "required": "Selecione o usuário do abastecimento.",
                "invalid_choice": "Selecione um usuário válido.",
            },
            "cisterna": {
                "required": "Selecione a cisterna abastecida.",
                "invalid_choice": "Selecione uma cisterna válida.",
            },
            "dataHora": {
                "required": "Informe a data e a hora do abastecimento.",
                "invalid": "Informe uma data e hora válidas.",
            },
            "quantidadeAgua": {
                "required": "Informe a quantidade de água.",
                "invalid": "Informe uma quantidade de água válida.",
            },
            "tipo": {
                "required": "Informe o tipo de abastecimento.",
                "max_length": "O tipo ultrapassou o tamanho permitido.",
            },
            "observacao": {
                "required": "Informe uma observação.",
                "max_length": "A observação ultrapassou o tamanho permitido.",
            },
            "status": {
                "required": "Informe o status do abastecimento.",
                "max_length": "O status ultrapassou o tamanho permitido.",
            },
        }

        widgets = {
            "usuario": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "cisterna": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "dataHora": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
            ),
            "quantidadeAgua": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.01",
                    "inputmode": "decimal",
                    "placeholder": "Quantidade em litros",
                }
            ),
            "tipo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": "255",
                    "placeholder": "Tipo do abastecimento",
                }
            ),
            "observacao": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": "4",
                    "maxlength": "255",
                    "data-contador-campo": "contador-observacao",
                    "placeholder": "Observação",
                }
            ),
            "status": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": "255",
                    "placeholder": "Ex.: Concluído",
                }
            ),
        }

    def __init__(self, *args, usuario_logado=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["usuario"].queryset = Usuario.objects.order_by(
            "nome",
            "username",
        )

        self.fields["cisterna"].queryset = Cisterna.objects.select_related(
            "usuario"
        ).order_by("id")

        if usuario_logado is not None and not usuario_logado.is_staff:
            campo_usuario = self.fields["usuario"]
            campo_usuario.queryset = Usuario.objects.filter(
                pk=usuario_logado.pk
            )
            campo_usuario.initial = usuario_logado.pk
            campo_usuario.disabled = True
            campo_usuario.help_text = (
                "O abastecimento é registrado no seu nome."
            )

            self.fields["cisterna"].queryset = Cisterna.objects.filter(
                usuario_id=usuario_logado.pk
            ).order_by("id")
            self.fields["cisterna"].help_text = "Escolha uma das suas cisternas."

        self.fields["dataHora"].input_formats = [
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
        ]

    def clean_quantidadeAgua(self):
        quantidade = self.cleaned_data.get("quantidadeAgua")

        if quantidade is not None and quantidade <= Decimal("0"):
            raise forms.ValidationError(
                "A quantidade de água deve ser maior que zero."
            )

        return quantidade

    def clean_tipo(self):
        tipo = self.cleaned_data.get("tipo", "").strip()

        if len(tipo) < 2:
            raise forms.ValidationError(
                "Informe um tipo de abastecimento válido."
            )

        return tipo

    def clean_observacao(self):
        observacao = self.cleaned_data.get("observacao", "").strip()

        if len(observacao) < 3:
            raise forms.ValidationError(
                "A observação deve possuir pelo menos 3 caracteres."
            )

        return observacao

    def clean_status(self):
        status = self.cleaned_data.get("status", "").strip()

        if len(status) < 2:
            raise forms.ValidationError(
                "Informe um status válido."
            )

        return status

    def clean(self):
        cleaned_data = super().clean()
        usuario = cleaned_data.get("usuario")
        cisterna = cleaned_data.get("cisterna")

        if (
            usuario is not None
            and cisterna is not None
            and cisterna.usuario_id != usuario.id
        ):
            self.add_error(
                "cisterna",
                "A cisterna selecionada não pertence ao usuário informado.",
            )

        return cleaned_data
