from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cisternas.models import Cisterna
from usuarios.models import Usuario

from .models import Abastecimento


class AbastecimentoCrudTests(TestCase):
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

    def test_abastecimento_crud_completo(self):
        response = self.client.get(reverse("abastecimento_listar"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Abastecimentos cadastrados")
        self.assertEqual(
            self.client.get(reverse("abastecimento_criar")).status_code,
            200,
        )

        abastecimento_data = timezone.now().strftime("%Y-%m-%dT%H:%M")
        response = self.client.post(
            reverse("abastecimento_criar"),
            {
                "usuario": str(self.usuario.pk),
                "cisterna": str(self.cisterna.pk),
                "dataHora": abastecimento_data,
                "quantidadeAgua": "40.00",
                "tipo": "Caminhão-pipa",
                "observacao": "Reposição inicial",
                "status": "Concluído",
            },
        )
        self.assertEqual(response.status_code, 302)
        abastecimento = Abastecimento.objects.get(tipo="Caminhão-pipa")
        response = self.client.get(
            reverse("abastecimento_editar", args=[abastecimento.pk])
        )
        self.assertContains(response, "Editar abastecimento")
        self.assertContains(response, "Salvar alterações")
        self.assertEqual(
            self.client.get(
                reverse("abastecimento_detalhar", args=[abastecimento.pk])
            ).status_code,
            200,
        )
        response = self.client.post(
            reverse("abastecimento_editar", args=[abastecimento.pk]),
            {
                "usuario": str(self.usuario.pk),
                "cisterna": str(self.cisterna.pk),
                "dataHora": abastecimento_data,
                "quantidadeAgua": "60.00",
                "tipo": "Caminhão-pipa",
                "observacao": "Reposição atualizada",
                "status": "Concluído",
            },
        )
        self.assertEqual(response.status_code, 302)
        abastecimento.refresh_from_db()
        self.assertEqual(abastecimento.quantidadeAgua, Decimal("60.00"))
        self.assertEqual(
            self.client.get(
                reverse("abastecimento_excluir", args=[abastecimento.pk])
            ).status_code,
            200,
        )
        self.client.post(
            reverse("abastecimento_excluir", args=[abastecimento.pk])
        )
        self.assertFalse(
            Abastecimento.objects.filter(pk=abastecimento.pk).exists()
        )