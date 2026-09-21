
from decimal import Decimal, InvalidOperation

from django import forms

from .models import Cisterna


class CisternaForm(forms.ModelForm):

    status = forms.ChoiceField(
        label="Status",
        choices=[
            ("", "Selecione o status da cisterna"),
            ("Ativa", "Ativa"),
            ("Inativa", "Inativa"),
            ("Em manutenção", "Em manutenção"),
            ("Em instalação", "Em instalação"),
            ("Interditada", "Interditada"),
        ],
        help_text="Selecione a situação atual da cisterna.",
        error_messages={
            "required": "Selecione o status da cisterna.",
            "invalid_choice": "Selecione um status válido.",
        },
        widget=forms.Select(
            attrs={
                "class": "campo-formulario",
            }
        ),
    )

    class Meta:
        model = Cisterna

        fields = (
            "usuario",
            "latitude",
            "longitude",
            "capacidade",
            "descricao",
            "status",
        )

        labels = {
            "usuario": "Usuário responsável",
            "latitude": "Latitude",
            "longitude": "Longitude",
            "capacidade": "Capacidade da cisterna",
            "descricao": "Descrição",
        }

        help_texts = {
            "usuario": "Selecione quem será responsável pela cisterna.",
            "latitude": "Valor entre -90 e 90. Pode ser preenchido pela localização do dispositivo.",
            "longitude": "Valor entre -180 e 180. Pode ser preenchido pela localização do dispositivo.",
            "capacidade": "Informe a capacidade total da cisterna em litros.",
            "descricao": "Use uma identificação curta para facilitar a listagem.",
        }

        error_messages = {
            "usuario": {
                "required": "Selecione o usuário responsável pela cisterna.",
                "invalid_choice": "Selecione um usuário válido.",
            },
            "latitude": {
                "required": "Informe a latitude da cisterna.",
                "invalid": "Informe uma latitude numérica válida.",
            },
            "longitude": {
                "required": "Informe a longitude da cisterna.",
                "invalid": "Informe uma longitude numérica válida.",
            },
            "capacidade": {
                "required": "Informe a capacidade da cisterna.",
                "invalid": "Informe uma capacidade numérica válida.",
            },
            "descricao": {
                "required": "Informe uma descrição para a cisterna.",
                "max_length": "A descrição ultrapassou o tamanho máximo permitido.",
            },
        }

        widgets = {
            "usuario": forms.Select(
                attrs={
                    "class": "campo-formulario",
                }
            ),

            "latitude": forms.NumberInput(
                attrs={
                    "class": "campo-formulario",
                    "step": "0.0000001",
                    "min": "-90",
                    "max": "90",
                    "inputmode": "decimal",
                    "placeholder": "Ex.: -14.2230000",
                    "autocomplete": "off",
                }
            ),

            "longitude": forms.NumberInput(
                attrs={
                    "class": "campo-formulario",
                    "step": "0.0000001",
                    "min": "-180",
                    "max": "180",
                    "inputmode": "decimal",
                    "placeholder": "Ex.: -42.7810000",
                    "autocomplete": "off",
                }
            ),

            "capacidade": forms.NumberInput(
                attrs={
                    "class": "campo-formulario",
                    "step": "0.01",
                    "min": "0.01",
                    "inputmode": "decimal",
                    "placeholder": "Capacidade em litros",
                }
            ),

            "descricao": forms.TextInput(
                attrs={
                    "class": "campo-formulario",
                    "maxlength": "255",
                    "placeholder": "Ex.: Cisterna principal",
                    "autocomplete": "off",
                }
            ),
        }

    def clean_latitude(self):
        latitude = self.cleaned_data.get("latitude")

        if latitude is None:
            return latitude

        try:
            latitude = Decimal(latitude)

        except (InvalidOperation, TypeError, ValueError) as exc:
            raise forms.ValidationError(
                "Informe uma latitude válida."
            ) from exc

        if latitude < Decimal("-90") or latitude > Decimal("90"):
            raise forms.ValidationError(
                "A latitude deve estar entre -90 e 90."
            )

        return latitude

    def clean_longitude(self):
        longitude = self.cleaned_data.get("longitude")

        if longitude is None:
            return longitude

        try:
            longitude = Decimal(longitude)

        except (InvalidOperation, TypeError, ValueError) as exc:
            raise forms.ValidationError(
                "Informe uma longitude válida."
            ) from exc

        if longitude < Decimal("-180") or longitude > Decimal("180"):
            raise forms.ValidationError(
                "A longitude deve estar entre -180 e 180."
            )

        return longitude

    def clean_capacidade(self):
        capacidade = self.cleaned_data.get("capacidade")

        if capacidade is None:
            return capacidade

        if capacidade <= Decimal("0"):
            raise forms.ValidationError(
                "A capacidade deve ser maior que zero."
            )

        return capacidade

    def clean_descricao(self):
        descricao = self.cleaned_data.get("descricao", "").strip()

        if len(descricao) < 3:
            raise forms.ValidationError(
                "A descrição deve possuir pelo menos 3 caracteres."
            )

        return descricao

    def clean_status(self):
        status = self.cleaned_data.get("status", "").strip()

        if len(status) < 2:
            raise forms.ValidationError(
                "Selecione um status válido."
            )

        return status