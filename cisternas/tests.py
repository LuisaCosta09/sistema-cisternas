from decimal import Decimal
from types import SimpleNamespace

from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from abastecimentos.models import Abastecimento
from monitoramentos.models import Monitoramento
from usuarios.models import Usuario

from .models import Cisterna


class CisternaCrudTests(TestCase):
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

    def test_cisterna_crud_completo(self):
        response = self.client.get(reverse("cisterna_listar"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cisternas cadastradas")
        self.assertContains(
            response,
            "https://www.google.com/maps/search/?api=1&amp;query=-12.3456789,-45.6789012",
        )

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

        response = self.client.get(
            reverse("cisterna_editar", args=[cisterna.pk])
        )
        self.assertContains(response, "Editar cisterna")
        self.assertContains(response, "Salvar alterações")

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

    def test_cisterna_sem_coordenadas_nao_exibe_link_de_mapa(self):
        cisterna_sem_coordenadas = SimpleNamespace(
            id=999,
            usuario=SimpleNamespace(nome="Usuário teste"),
            latitude=None,
            longitude=None,
            capacidade=Decimal("100.00"),
            descricao="Localização não informada",
            status="Ativa",
            pk=999,
        )

        html = render_to_string(
            "cisternas/cisterna_listar.html",
            {
                "titulo_pagina": "Cisternas cadastradas",
                "quantidade_cisternas": 1,
                "cisternas": [cisterna_sem_coordenadas],
            },
        )

        self.assertIn("Localização indisponível", html)
        self.assertNotIn("google.com/maps", html)

    def test_cisterna_permite_trocar_responsavel_sem_registros_dependentes(self):
        self.usuario.is_staff = True
        self.usuario.save(update_fields=("is_staff",))
        self.monitoramento.delete()
        novo_usuario = Usuario.objects.create_user(
            username="marina",
            email="marina@email.com",
            password="senha123",
            nome="Marina",
            cpf="52998224725",
        )

        response = self.client.post(
            reverse("cisterna_editar", args=[self.cisterna.pk]),
            {
                "usuario": str(novo_usuario.pk),
                "latitude": "-12.3456789",
                "longitude": "-45.6789012",
                "capacidade": "1200.00",
                "descricao": "Cisterna principal",
                "status": "Ativa",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.cisterna.refresh_from_db()
        self.assertEqual(self.cisterna.usuario_id, novo_usuario.pk)

    def test_cisterna_impede_trocar_responsavel_com_monitoramento(self):
        self.usuario.is_staff = True
        self.usuario.save(update_fields=("is_staff",))
        novo_usuario = Usuario.objects.create_user(
            username="marina",
            email="marina@email.com",
            password="senha123",
            nome="Marina",
            cpf="52998224725",
        )

        response = self.client.post(
            reverse("cisterna_editar", args=[self.cisterna.pk]),
            {
                "usuario": str(novo_usuario.pk),
                "latitude": "-12.3456789",
                "longitude": "-45.6789012",
                "capacidade": "1200.00",
                "descricao": "Cisterna principal",
                "status": "Ativa",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Não é possível alterar o responsável")
        self.cisterna.refresh_from_db()
        self.assertEqual(self.cisterna.usuario_id, self.usuario.pk)

    def test_cisterna_impede_trocar_responsavel_com_abastecimento(self):
        self.usuario.is_staff = True
        self.usuario.save(update_fields=("is_staff",))
        Abastecimento.objects.create(
            usuario=self.usuario,
            cisterna=self.cisterna,
            dataHora=timezone.now(),
            quantidadeAgua=Decimal("20.00"),
            tipo="Caminhão-pipa",
            observacao="Reposição de água",
            status="Concluído",
        )
        novo_usuario = Usuario.objects.create_user(
            username="marina",
            email="marina@email.com",
            password="senha123",
            nome="Marina",
            cpf="52998224725",
        )

        response = self.client.post(
            reverse("cisterna_editar", args=[self.cisterna.pk]),
            {
                "usuario": str(novo_usuario.pk),
                "latitude": "-12.3456789",
                "longitude": "-45.6789012",
                "capacidade": "1200.00",
                "descricao": "Cisterna principal",
                "status": "Ativa",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Não é possível alterar o responsável")
        self.cisterna.refresh_from_db()
        self.assertEqual(self.cisterna.usuario_id, self.usuario.pk)