from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Cisterna, Monitoramento, Usuario


class CisternaMonitoramentoCrudTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="pedro",
            email="pedro@email.com",
            password="senha123",
            nome="Pedro",
            cpf="12345678909",
        )

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

    def test_cisterna_crud_completo(self):
        response = self.client.get(reverse("cisterna_listar"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cisternas cadastradas")

        response = self.client.get(reverse("cisterna_criar"))
        self.assertEqual(response.status_code, 200)

        payload = {
            "usuario": str(self.usuario.pk),
            "latitude": "-10.0000000",
            "longitude": "-40.0000000",
            "capacidade": "1500.50",
            "descricao": "Cisterna nova",
            "status": "Em manutenção",
        }

        response = self.client.post(reverse("cisterna_criar"), payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Cisterna.objects.filter(descricao="Cisterna nova").exists()
        )

        cisterna = Cisterna.objects.get(descricao="Cisterna nova")

        response = self.client.get(reverse("cisterna_detalhar", args=[cisterna.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cisterna nova")

        payload_update = {
            "usuario": str(self.usuario.pk),
            "latitude": "-11.1111111",
            "longitude": "-41.1111111",
            "capacidade": "1800.00",
            "descricao": "Cisterna atualizada",
            "status": "Ativa",
        }

        response = self.client.post(
            reverse("cisterna_editar", args=[cisterna.pk]),
            payload_update,
        )
        self.assertEqual(response.status_code, 302)
        cisterna.refresh_from_db()
        self.assertEqual(cisterna.descricao, "Cisterna atualizada")

        response = self.client.post(
            reverse("cisterna_excluir", args=[cisterna.pk]),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Cisterna.objects.filter(pk=cisterna.pk).exists())

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
            "situacao": "Leitura normal",
        }

        response = self.client.post(reverse("monitoramento_criar"), payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Monitoramento.objects.filter(situacao="Leitura normal").exists()
        )

        monitoramento = Monitoramento.objects.get(situacao="Leitura normal")

        response = self.client.get(
            reverse("monitoramento_detalhar", args=[monitoramento.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leitura normal")

        payload_update = {
            "usuario": str(self.usuario.pk),
            "cisterna": str(self.cisterna.pk),
            "dataHora": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            "nivelAgua": "75.00",
            "consumo": "20.00",
            "situacao": "Leitura atualizada",
        }

        response = self.client.post(
            reverse("monitoramento_editar", args=[monitoramento.pk]),
            payload_update,
        )
        self.assertEqual(response.status_code, 302)
        monitoramento.refresh_from_db()
        self.assertEqual(monitoramento.situacao, "Leitura atualizada")

        response = self.client.post(
            reverse("monitoramento_excluir", args=[monitoramento.pk]),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Monitoramento.objects.filter(pk=monitoramento.pk).exists()
        )
