from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Cisterna, Monitoramento, Usuario


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
            "latitude": (
                "Valor entre -90 e 90. Pode ser preenchido pela "
                "localização do dispositivo."
            ),
            "longitude": (
                "Valor entre -180 e 180. Pode ser preenchido pela "
                "localização do dispositivo."
            ),
            "capacidade": "Informe a capacidade total da cisterna em litros.",
            "descricao": (
                "Use uma identificação curta para facilitar a listagem."
            ),
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
                "max_length": (
                    "A descrição ultrapassou o tamanho máximo permitido."
                ),
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


class UsuarioForm(UserCreationForm):
    email = forms.EmailField(
        label="E-mail",
        required=True,
        max_length=254,
        help_text=(
            "Informe um e-mail válido e que ainda não esteja cadastrado."
        ),
        widget=forms.EmailInput(
            attrs={
                "class": "campo-formulario",
                "autocomplete": "email",
                "placeholder": "nome@exemplo.com",
            }
        ),
        error_messages={
            "required": "Informe o e-mail do usuário.",
            "invalid": "Informe um endereço de e-mail válido.",
        },
    )

    class Meta(UserCreationForm.Meta):
        model = Usuario

        fields = (
            "username",
            "email",
            "nome",
            "cpf",
            "password1",
            "password2",
        )

        labels = {
            "username": "Nome de usuário",
            "nome": "Nome completo",
            "cpf": "CPF",
        }

        help_texts = {
            "username": "Use um identificador único para entrar no sistema.",
            "nome": "Informe o nome completo do usuário.",
            "cpf": "Digite somente os 11 números do CPF.",
        }

        error_messages = {
            "username": {
                "required": "Informe um nome de usuário.",
                "unique": "Este nome de usuário já está em uso.",
                "max_length": (
                    "O nome de usuário ultrapassou o tamanho permitido."
                ),
            },
            "nome": {
                "required": "Informe o nome completo.",
                "max_length": "O nome ultrapassou o tamanho permitido.",
            },
            "cpf": {
                "required": "Informe o CPF.",
                "unique": (
                    "Já existe um usuário cadastrado com este CPF."
                ),
                "max_length": (
                    "O CPF deve possuir no máximo 11 caracteres."
                ),
            },
        }

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "campo-formulario",
                    "autocomplete": "username",
                    "placeholder": "Nome de usuário",
                }
            ),
            "nome": forms.TextInput(
                attrs={
                    "class": "campo-formulario",
                    "maxlength": "255",
                    "autocomplete": "name",
                    "placeholder": "Nome completo",
                }
            ),
            "cpf": forms.TextInput(
                attrs={
                    "class": "campo-formulario",
                    "maxlength": "11",
                    "inputmode": "numeric",
                    "autocomplete": "off",
                    "placeholder": "Somente números",
                }
            ),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)

        self.fields["password1"].label = "Senha"
        self.fields["password2"].label = "Confirmação da senha"

        self.fields["password1"].help_text = (
            "Crie uma senha que atenda às regras de segurança do Django."
        )

        self.fields["password2"].help_text = (
            "Digite novamente a mesma senha para confirmar."
        )

        self.fields["password1"].widget.attrs.update(
            {
                "class": "campo-formulario",
                "autocomplete": "new-password",
                "placeholder": "Senha",
            }
        )

        self.fields["password2"].widget.attrs.update(
            {
                "class": "campo-formulario",
                "autocomplete": "new-password",
                "placeholder": "Repita a senha",
            }
        )

    def clean_nome(self):
        nome = self.cleaned_data.get("nome", "").strip()

        if len(nome) < 3:
            raise forms.ValidationError(
                "Informe o nome completo do usuário."
            )

        return nome

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()

        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Já existe um usuário cadastrado com este e-mail."
            )

        return email

    def clean_cpf(self):
        cpf_recebido = self.cleaned_data.get("cpf", "")

        cpf = "".join(
            caractere
            for caractere in str(cpf_recebido)
            if caractere.isdigit()
        )

        if len(cpf) != 11:
            raise forms.ValidationError(
                "O CPF deve possuir exatamente 11 números."
            )

        if cpf == cpf[0] * 11:
            raise forms.ValidationError(
                "Informe um CPF válido."
            )

        soma_primeiro = sum(
            int(cpf[indice]) * (10 - indice)
            for indice in range(9)
        )

        resto_primeiro = (soma_primeiro * 10) % 11
        primeiro_digito = (
            0 if resto_primeiro == 10 else resto_primeiro
        )

        soma_segundo = sum(
            int(cpf[indice]) * (11 - indice)
            for indice in range(10)
        )

        resto_segundo = (soma_segundo * 10) % 11
        segundo_digito = (
            0 if resto_segundo == 10 else resto_segundo
        )

        if (
            int(cpf[9]) != primeiro_digito
            or int(cpf[10]) != segundo_digito
        ):
            raise forms.ValidationError(
                "Informe um CPF válido."
            )

        return cpf


class MonitoramentoForm(forms.ModelForm):
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
            "nivelAgua": forms.NumberInput(
                attrs={
                    "class": "campo-formulario",
                    "step": "0.01",
                    "min": "0",
                    "inputmode": "decimal",
                    "placeholder": "Nível medido",
                }
            ),
            "consumo": forms.NumberInput(
                attrs={
                    "class": "campo-formulario",
                    "step": "0.01",
                    "min": "0",
                    "inputmode": "decimal",
                    "placeholder": "Consumo medido",
                }
            ),
            "situacao": forms.TextInput(
                attrs={
                    "class": "campo-formulario",
                    "maxlength": "255",
                    "placeholder": "Situação da cisterna",
                }
            ),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)

        self.fields["usuario"].queryset = Usuario.objects.order_by(
            "nome",
            "username",
        )

        self.fields["cisterna"].queryset = (
            Cisterna.objects.select_related("usuario").order_by("id")
        )

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