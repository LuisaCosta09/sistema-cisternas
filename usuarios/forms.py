from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

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
                "class": "form-control",
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
                    "class": "form-control",
                    "autocomplete": "username",
                    "placeholder": "Nome de usuário",
                }
            ),
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": "255",
                    "autocomplete": "name",
                    "placeholder": "Nome completo",
                }
            ),
            "cpf": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": "11",
                    "inputmode": "numeric",
                    "autocomplete": "off",
                    "placeholder": "Somente números",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
                "class": "form-control",
                "autocomplete": "new-password",
                "placeholder": "Senha",
            }
        )

        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
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



class UsuarioAtualizacaoForm(forms.ModelForm):
    email = forms.EmailField(
        label="E-mail",
        required=True,
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "autocomplete": "email",
            }
        ),
    )

    class Meta:
        model = Usuario
        fields = ("username", "email", "nome", "cpf")

        labels = {
            "username": "Nome de usuário",
            "nome": "Nome completo",
            "cpf": "CPF",
        }

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "username",
                }
            ),
            "nome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": "255",
                    "autocomplete": "name",
                }
            ),
            "cpf": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "maxlength": "11",
                    "inputmode": "numeric",
                    "autocomplete": "off",
                }
            ),
        }

    def clean_nome(self):
        nome = self.cleaned_data.get("nome", "").strip()

        if len(nome) < 3:
            raise forms.ValidationError(
                "Informe o nome completo do usuário."
            )

        return nome

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        usuarios_com_email = Usuario.objects.filter(email__iexact=email)

        if self.instance.pk:
            usuarios_com_email = usuarios_com_email.exclude(
                pk=self.instance.pk
            )

        if usuarios_com_email.exists():
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

        if len(cpf) != 11 or cpf == cpf[0] * 11:
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
