from django.db import models
from django.contrib.auth.models import User


class Usuario(User):
    nome = models.CharField(max_length=255)
    cpf = models.BigIntegerField()

    def _str_(self):
        return f"{self.nome} ({self.username})"

class Cisterna(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="cisternas",
    )
    latitude = models.CharField(max_length=255)
    capacidade = models.FloatField()
    descricao = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)

    def __str__(self):
        return f"Cisterna {self.id}"


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
    nivelAgua = models.FloatField()
    consumo = models.FloatField()
    situacao = models.CharField(max_length=255)

    def __str__(self):
        return f"Monitoramento {self.id}"





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
    quantidadeAgua = models.FloatField()
    tipo = models.CharField(max_length=255)
    observacao = models.CharField(max_length=255)
    status = models.CharField(max_length=255)

    def __str__(self):
        return f"Abastecimento {self.id}"