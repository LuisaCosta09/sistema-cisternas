from django.db import models
from django.contrib.auth.models import User


class Usuario(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="usuario"
    )

    def __str__(self):
        return self.user.username


class Cisterna(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="cisternas"
    )

    localizacao = models.CharField(max_length=255)
    capacidade = models.FloatField()
    descricao = models.TextField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Cisterna {self.id} - {self.localizacao}"


class Monitoramento(models.Model):
    cisterna = models.ForeignKey(
        Cisterna,
        on_delete=models.CASCADE,
        related_name="monitoramentos"
    )

    dataHora = models.DateTimeField()
    nivelAgua = models.FloatField()
    consumo = models.FloatField()
    situacao = models.CharField(max_length=50)

    def __str__(self):
        return f"Monitoramento {self.id} - Cisterna {self.cisterna.id}"


class Relatorio(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="relatorios"
    )

    cisterna = models.ForeignKey(
        Cisterna,
        on_delete=models.CASCADE,
        related_name="relatorios"
    )

    periodoInicio = models.DateField()
    periodoFim = models.DateField()
    formato = models.CharField(max_length=20)
    dataGeracao = models.DateTimeField()

    def __str__(self):
        return f"Relatório {self.id}"


class Alerta(models.Model):
    cisterna = models.ForeignKey(
        Cisterna,
        on_delete=models.CASCADE,
        related_name="alertas"
    )

    tipo = models.CharField(max_length=50)
    mensagem = models.TextField()
    status = models.CharField(max_length=50)
    dataHora = models.DateTimeField()

    def __str__(self):
        return f"Alerta {self.id} - {self.tipo}"


class Abastecimento(models.Model):
    cisterna = models.ForeignKey(
        Cisterna,
        on_delete=models.CASCADE,
        related_name="abastecimentos"
    )

    dataHora = models.DateTimeField()
    quantidadeAgua = models.FloatField()
    tipo = models.CharField(max_length=50)
    observacao = models.TextField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"Abastecimento {self.id}"