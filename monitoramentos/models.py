from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from cisternas.models import Cisterna
from usuarios.models import Usuario


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