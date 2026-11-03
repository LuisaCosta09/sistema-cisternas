from django.db import models

from cisternas.models import Cisterna


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