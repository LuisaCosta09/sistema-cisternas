from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Usuario(User):
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=11, unique=True)

    class Meta:
        ordering = ("nome", "username")

    def __str__(self):
        return f"{self.nome} ({self.username})"


class Cisterna(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="cisternas",
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        validators=[
            MinValueValidator(Decimal("-90")),
            MaxValueValidator(Decimal("90")),
        ],
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        validators=[
            MinValueValidator(Decimal("-180")),
            MaxValueValidator(Decimal("180")),
        ],
    )

    capacidade = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
    )

    descricao = models.CharField(max_length=255)
    status = models.CharField(max_length=20)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"Cisterna {self.id} - {self.usuario.nome}"


class Monitoramento(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="monitoramentos",
    )

    cisterna = models.ForeignKey(
        Cisterna,
        on_delete=models.CASCADE,
        related_name="monitoramentos",
    )

    dataHora = models.DateTimeField()

    nivelAgua = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
    )

    consumo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0")),
        ],
    )

    situacao = models.CharField(max_length=255)

    class Meta:
        ordering = ("-dataHora", "-id")

    def clean(self):
        super().clean()

        if (
            self.usuario_id
            and self.cisterna_id
            and self.cisterna.usuario_id != self.usuario_id
        ):
            raise ValidationError(
                {
                    "cisterna": (
                        "A cisterna selecionada não pertence ao usuário informado."
                    )
                }
            )

    def __str__(self):
        return f"Monitoramento {self.id} - Cisterna {self.cisterna_id}"


class Alerta(models.Model):
    cisterna = models.ForeignKey(
        Cisterna,
        on_delete=models.CASCADE,
        related_name="alertas",
    )

    tipo = models.CharField(max_length=255)
    mensagem = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    dataHora = models.DateTimeField()

    class Meta:
        ordering = ("-dataHora", "-id")

    def __str__(self):
        return f"Alerta {self.id} - {self.tipo}"


class Abastecimento(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="abastecimentos",
    )

    cisterna = models.ForeignKey(
        Cisterna,
        on_delete=models.CASCADE,
        related_name="abastecimentos",
    )

    dataHora = models.DateTimeField()
    quantidadeAgua = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
    )
    tipo = models.CharField(max_length=255)
    observacao = models.CharField(max_length=255)
    status = models.CharField(max_length=255)

    class Meta:
        ordering = ("-dataHora", "-id")

    def clean(self):
        super().clean()

        if (
            self.usuario_id
            and self.cisterna_id
            and self.cisterna.usuario_id != self.usuario_id
        ):
            raise ValidationError(
                {
                    "cisterna": (
                        "A cisterna selecionada não pertence ao usuário informado."
                    )
                }
            )

    def __str__(self):
        return f"Abastecimento {self.id} - Cisterna {self.cisterna_id}"
