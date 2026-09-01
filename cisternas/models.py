from django.conf import settings
from django.db import models


class Usuario(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="usuario",
        primary_key=True,
    )
    nome = models.CharField(max_length=255)
    cpf = models.BigIntegerField()

    def __str__(self):
        return f"{self.nome} ({self.user.username})"


class Cisterna(models.Model):
    id = models.AutoField(primary_key=True)
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
    id = models.AutoField(primary_key=True)
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
    id = models.AutoField(primary_key=True)
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
    id = models.AutoField(primary_key=True)
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