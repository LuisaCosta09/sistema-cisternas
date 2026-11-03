from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cisternas.models import Cisterna
from usuarios.models import Usuario

from .models import Alerta


class AlertaCrudTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="pedro",
            email="pedro@email.com",
            password="senha123",
            nome="Pedro",
            cpf="12345678909",
        )

        self.client.force_login(self.usuario)

        self.cisterna = Cisterna.objects.create(
            usuario=self.usuario,
            latitude=Decimal("-12.3456789"),
            longitude=Decimal("-45.6789012"),
            capacidade=Decimal("1200.00"),
            descricao="Cisterna principal",
            status="Ativa",
        )

    def test_alerta_crud_completo(self):
        response = self.client.get(reverse("alerta_listar"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alertas cadastrados")
        self.assertEqual(
            self.client.get(reverse("alerta_criar")).status_code,
            200,
        )

        alerta_data = timezone.now().strftime("%Y-%m-%dT%H:%M")
        response = self.client.post(
            reverse("alerta_criar"),
            {
                "cisterna": str(self.cisterna.pk),
                "tipo": "Nível baixo",
                "mensagem": "Nível abaixo do esperado",
                "status": "Pendente",
                "dataHora": alerta_data,
            },
        )
        self.assertEqual(response.status_code, 302)
        alerta = Alerta.objects.get(tipo="Nível baixo")
        response = self.client.get(
            reverse("alerta_editar", args=[alerta.pk])
        )
        self.assertContains(response, "Editar alerta")
        self.assertContains(response, "Salvar alterações")
        self.assertEqual(
            self.client.get(
                reverse("alerta_detalhar", args=[alerta.pk])
            ).status_code,
            200,
        )
        response = self.client.post(
            reverse("alerta_editar", args=[alerta.pk]),
            {
                "cisterna": str(self.cisterna.pk),
                "tipo": "Nível médio baixo",
                "mensagem": "Nível muito abaixo do esperado",
                "status": "Em análise",
                "dataHora": alerta_data,
            },
        )
        self.assertEqual(response.status_code, 302)
        alerta.refresh_from_db()
        self.assertEqual(alerta.tipo, "Nível médio baixo")
        self.assertEqual(
            self.client.get(
                reverse("alerta_excluir", args=[alerta.pk])
            ).status_code,
            200,
        )
        self.client.post(reverse("alerta_excluir", args=[alerta.pk]))
        self.assertFalse(Alerta.objects.filter(pk=alerta.pk).exists())