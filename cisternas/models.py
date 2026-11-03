from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from usuarios.models import Usuario


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

    def clean(self):
        super().clean()

        responsavel_alterado = (
            self.pk
            and type(self).objects.filter(pk=self.pk)
            .exclude(usuario_id=self.usuario_id)
            .exists()
        )

        if responsavel_alterado and (
            self.monitoramentos.exists() or self.abastecimentos.exists()
        ):
            raise ValidationError(
                {
                    "usuario": (
                        "Não é possível alterar o responsável enquanto "
                        "a cisterna possuir monitoramentos ou abastecimentos."
                    )
                }
            )

    def __str__(self):
        return f"Cisterna {self.id} - {self.usuario.nome}"