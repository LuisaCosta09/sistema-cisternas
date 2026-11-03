from django import forms
from cisternas.models import Cisterna
from usuarios.models import Usuario
from .models import Monitoramento

class MonitoramentoForm(forms.ModelForm):

    situacao = forms.ChoiceField(
        label="Situação",
        choices=[
            ("", "Selecione a situação"),
            ("Normal", "Normal"),
            ("Atenção", "Atenção"),
            ("Crítica", "Crítica"),
        ],
        help_text="Selecione a situação encontrada na leitura.",
        error_messages={
            "required": "Selecione a situação do monitoramento.",
            "invalid_choice": "Selecione uma situação válida.",
        },
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    
    class Meta:
        model = Monitoramento

        fields = (
            "usuario",
            "cisterna",
            "dataHora",
            "nivelAgua",
            "consumo",
            "situacao",
        )

        labels = {
            "usuario": "Usuário",
            "cisterna": "Cisterna",
            "dataHora": "Data e hora",
            "nivelAgua": "Nível da água",
            "consumo": "Consumo",
            "situacao": "Situação",
        }

        help_texts = {
            "usuario": (
                "Selecione o usuário relacionado ao monitoramento."
            ),
            "cisterna": (
                "A cisterna deve pertencer ao usuário selecionado."
            ),
            "dataHora": (
                "Informe quando a leitura foi realizada."
            ),
            "nivelAgua": (
                "Informe um valor igual ou maior que zero."
            ),
            "consumo": (
                "Informe um valor igual ou maior que zero."
            ),
            "situacao": (
                "Registre uma descrição curta da situação encontrada."
            ),
        }

        error_messages = {
            "usuario": {
                "required": "Selecione o usuário do monitoramento.",
                "invalid_choice": "Selecione um usuário válido.",
            },
            "cisterna": {
                "required": "Selecione a cisterna monitorada.",
                "invalid_choice": "Selecione uma cisterna válida.",
            },
            "dataHora": {
                "required": (
                    "Informe a data e a hora do monitoramento."
                ),
                "invalid": "Informe uma data e hora válidas.",
            },
            "nivelAgua": {
                "required": "Informe o nível da água.",
                "invalid": "Informe um nível de água válido.",
            },
            "consumo": {
                "required": "Informe o consumo.",
                "invalid": "Informe um consumo válido.",
            },
            "situacao": {
                "required": "Informe a situação do monitoramento.",
                "max_length": (
                    "A situação ultrapassou o tamanho permitido."
                ),
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
            "nivelAgua": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "inputmode": "decimal",
                    "placeholder": "Nível medido",
                }
            ),
            "consumo": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "inputmode": "decimal",
                    "placeholder": "Consumo medido",
                }
            ),
        }

    def __init__(self, *args, usuario_logado=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["usuario"].queryset = Usuario.objects.order_by(
            "nome",
            "username",
        )

        self.fields["cisterna"].queryset = (
            Cisterna.objects.select_related("usuario").order_by("id")
        )

        if usuario_logado is not None and not usuario_logado.is_staff:
            campo_usuario = self.fields["usuario"]
            campo_usuario.queryset = Usuario.objects.filter(
                pk=usuario_logado.pk
            )
            campo_usuario.initial = usuario_logado.pk
            campo_usuario.disabled = True
            campo_usuario.help_text = (
                "O monitoramento é registrado no seu nome."
            )

            self.fields["cisterna"].queryset = Cisterna.objects.filter(
                usuario_id=usuario_logado.pk
            ).order_by("id")
            self.fields["cisterna"].help_text = "Escolha uma das suas cisternas."

        self.fields["dataHora"].input_formats = [
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
        ]

    def clean_nivelAgua(self):
        nivel_agua = self.cleaned_data.get("nivelAgua")

        if nivel_agua is not None and nivel_agua < 0:
            raise forms.ValidationError(
                "O nível da água não pode ser negativo."
            )

        return nivel_agua

    def clean_consumo(self):
        consumo = self.cleaned_data.get("consumo")

        if consumo is not None and consumo < 0:
            raise forms.ValidationError(
                "O consumo não pode ser negativo."
            )

        return consumo

    def clean_situacao(self):
        situacao = self.cleaned_data.get("situacao", "").strip()

        if len(situacao) < 2:
            raise forms.ValidationError(
                "Informe uma situação válida."
            )

        return situacao

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
