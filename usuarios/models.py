from django.contrib.auth.models import User
from django.db import models


class Usuario(User):
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=11, unique=True)

    class Meta:
        ordering = ("nome", "username")

    def __str__(self):
        return f"{self.nome} ({self.username})"