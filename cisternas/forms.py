
from decimal import Decimal, InvalidOperation

from django import forms

from .models import Abastecimento, Alerta, Cisterna, Usuario


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


class AlertaForm(forms.ModelForm):

    class Meta:
        model = Alerta

        fields = (
            "cisterna",
            "tipo",
            "mensagem",
            "status",
            "dataHora",
        )

        labels = {
            "cisterna": "Cisterna",
            "tipo": "Tipo do alerta",
            "mensagem": "Mensagem",
            "status": "Status",
            "dataHora": "Data e hora",
        }

        help_texts = {
            "cisterna": "Selecione a cisterna relacionada ao alerta.",
            "tipo": "Informe uma identificação curta para o tipo de alerta.",
            "mensagem": "Descreva de forma objetiva o motivo do alerta.",
            "status": "Informe a situação atual do alerta.",
            "dataHora": "Informe quando o alerta foi registrado.",
        }

        error_messages = {
            "cisterna": {
                "required": "Selecione a cisterna relacionada ao alerta.",
                "invalid_choice": "Selecione uma cisterna válida.",
            },
            "tipo": {
                "required": "Informe o tipo do alerta.",
                "max_length": "O tipo do alerta ultrapassou o tamanho permitido.",
            },
            "mensagem": {
                "required": "Informe a mensagem do alerta.",
                "max_length": "A mensagem ultrapassou o tamanho permitido.",
            },
            "status": {
                "required": "Informe o status do alerta.",
                "max_length": "O status ultrapassou o tamanho permitido.",
            },
            "dataHora": {
                "required": "Informe a data e a hora do alerta.",
                "invalid": "Informe uma data e hora válidas.",
            },
        }

        widgets = {
            "cisterna": forms.Select(
                attrs={
                    "class": "campo-formulario",
                }
            ),
            "tipo": forms.TextInput(
                attrs={
                    "class": "campo-formulario",
                    "maxlength": "255",
                    "placeholder": "Ex.: Nível baixo",
                }
            ),
            "mensagem": forms.Textarea(
                attrs={
                    "class": "campo-formulario",
                    "rows": "4",
                    "maxlength": "255",
                    "data-contador-campo": "contador-mensagem",
                    "placeholder": "Descreva o alerta",
                }
            ),
            "status": forms.TextInput(
                attrs={
                    "class": "campo-formulario",
                    "maxlength": "255",
                    "placeholder": "Ex.: Pendente",
                }
            ),
            "dataHora": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "class": "campo-formulario",
                    "type": "datetime-local",
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["cisterna"].queryset = Cisterna.objects.select_related(
            "usuario"
        ).order_by("id")

        self.fields["dataHora"].input_formats = [
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
        ]

    def clean_tipo(self):
        tipo = self.cleaned_data.get("tipo", "").strip()

        if len(tipo) < 2:
            raise forms.ValidationError(
                "Informe um tipo de alerta válido."
            )

        return tipo

    def clean_mensagem(self):
        mensagem = self.cleaned_data.get("mensagem", "").strip()

        if len(mensagem) < 5:
            raise forms.ValidationError(
                "A mensagem deve possuir pelo menos 5 caracteres."
            )

        return mensagem

    def clean_status(self):
        status = self.cleaned_data.get("status", "").strip()

        if len(status) < 2:
            raise forms.ValidationError(
                "Informe um status válido."
            )

        return status


class AbastecimentoForm(forms.ModelForm):

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
                    "class": "campo-formulario",
                }
            ),
            "cisterna": forms.Select(
                attrs={
                    "class": "campo-formulario",
                }
            ),
            "dataHora": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "class": "campo-formulario",
                    "type": "datetime-local",
                },
            ),
            "quantidadeAgua": forms.NumberInput(
                attrs={
                    "class": "campo-formulario",
                    "step": "0.01",
                    "min": "0.01",
                    "inputmode": "decimal",
                    "placeholder": "Quantidade em litros",
                }
            ),
            "tipo": forms.TextInput(
                attrs={
                    "class": "campo-formulario",
                    "maxlength": "255",
                    "placeholder": "Tipo do abastecimento",
                }
            ),
            "observacao": forms.Textarea(
                attrs={
                    "class": "campo-formulario",
                    "rows": "4",
                    "maxlength": "255",
                    "data-contador-campo": "contador-observacao",
                    "placeholder": "Observação",
                }
            ),
            "status": forms.TextInput(
                attrs={
                    "class": "campo-formulario",
                    "maxlength": "255",
                    "placeholder": "Ex.: Concluído",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["usuario"].queryset = Usuario.objects.order_by(
            "nome",
            "username",
        )

        self.fields["cisterna"].queryset = Cisterna.objects.select_related(
            "usuario"
        ).order_by("id")

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
