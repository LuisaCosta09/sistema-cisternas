from django import forms
from cisternas.models import Cisterna
from .models import Alerta

class AlertaForm(forms.ModelForm):

    tipo = forms.ChoiceField(
        label="Tipo do alerta",
        choices=[
            ("", "Selecione o tipo do alerta"),
            ("Cheia", "Cheia"),
            ("Nível médio alto", "Nível médio alto"),
            ("Nível OK", "Nível OK"),
            ("Nível médio baixo", "Nível médio baixo"),
            ("Nível baixo", "Nível baixo"),
        ],
        help_text="Selecione o nível da água que gerou o alerta.",
        error_messages={
            "required": "Selecione o tipo do alerta.",
            "invalid_choice": "Selecione um tipo válido.",
        },
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    status = forms.ChoiceField(
        label="Status",
        choices=[
            ("", "Selecione o status do alerta"),
            ("Pendente", "Pendente"),
            ("Em análise", "Em análise"),
            ("Resolvido", "Resolvido"),
        ],
        help_text="Selecione a situação atual do alerta.",
        error_messages={
            "required": "Selecione o status do alerta.",
            "invalid_choice": "Selecione um status válido.",
        },
        widget=forms.Select(attrs={"class": "form-select"}),
    )

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
                    "class": "form-select",
                }
            ),
            "tipo": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": "255",
                    "placeholder": "Ex.: Nível baixo",
                }
            ),
            "mensagem": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": "4",
                    "maxlength": "255",
                    "data-contador-campo": "contador-mensagem",
                    "placeholder": "Descreva o alerta",
                }
            ),
            "status": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": "255",
                    "placeholder": "Ex.: Pendente",
                }
            ),
            "dataHora": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
            ),
        }

    def __init__(self, *args, usuario_logado=None, **kwargs):
        super().__init__(*args, **kwargs)

        cisternas = Cisterna.objects.select_related("usuario").order_by("id")

        if usuario_logado is not None and not usuario_logado.is_staff:
            cisternas = cisternas.filter(usuario_id=usuario_logado.pk)
            self.fields["cisterna"].help_text = "Escolha uma das suas cisternas."

        self.fields["cisterna"].queryset = cisternas

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