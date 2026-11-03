from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cisternas.models import Cisterna
from usuarios.models import Usuario

from .models import Monitoramento


class MonitoramentoCrudTests(TestCase):
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

        self.monitoramento = Monitoramento.objects.create(
            usuario=self.usuario,
            cisterna=self.cisterna,
            dataHora=timezone.now(),
            nivelAgua=Decimal("50.00"),
            consumo=Decimal("10.00"),
            situacao="Estável",
        )

    def test_monitoramento_crud_completo(self):
        response = self.client.get(reverse("monitoramento_listar"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Monitoramentos cadastrados")

        response = self.client.get(reverse("monitoramento_criar"))
        self.assertEqual(response.status_code, 200)

        payload = {
            "usuario": str(self.usuario.pk),
            "cisterna": str(self.cisterna.pk),
            "dataHora": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "nivelAgua": "60.00",
            "consumo": "15.00",
            "situacao": "Normal",
        }

        response = self.client.post(reverse("monitoramento_criar"), payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Monitoramento.objects.filter(situacao="Normal").exists()
        )

        monitoramento = Monitoramento.objects.get(situacao="Normal")

        response = self.client.get(
            reverse("monitoramento_editar", args=[monitoramento.pk])
        )
        self.assertContains(response, "Editar monitoramento")
        self.assertContains(response, "Salvar alterações")

        response = self.client.get(
            reverse("monitoramento_detalhar", args=[monitoramento.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Normal")

        payload_update = {
            "usuario": str(self.usuario.pk),
            "cisterna": str(self.cisterna.pk),
            "dataHora": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "nivelAgua": "75.00",
            "consumo": "20.00",
            "situacao": "Atenção",
        }

        response = self.client.post(
            reverse("monitoramento_editar", args=[monitoramento.pk]),
            payload_update,
        )
        self.assertEqual(response.status_code, 302)
        monitoramento.refresh_from_db()
        self.assertEqual(monitoramento.situacao, "Atenção")

        response = self.client.post(
            reverse("monitoramento_excluir", args=[monitoramento.pk]),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Monitoramento.objects.filter(pk=monitoramento.pk).exists()
        )

    def test_monitoramento_lista_estado_vazio(self):
        self.monitoramento.delete()

        response = self.client.get(reverse("monitoramento_listar"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nenhum monitoramento cadastrado")