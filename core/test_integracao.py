from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from abastecimentos.forms import AbastecimentoForm
from abastecimentos.models import Abastecimento
from alertas.models import Alerta
from cisternas.models import Cisterna
from monitoramentos.forms import MonitoramentoForm
from monitoramentos.models import Monitoramento
from usuarios.models import Usuario


class IntegracaoEntreAppsTests(TestCase):
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

    def test_exclusao_de_usuario_remove_todos_os_dependentes_em_cascata(self):
        self.usuario.is_staff = True
        self.usuario.save(update_fields=("is_staff",))

        alerta = Alerta.objects.create(
            cisterna=self.cisterna,
            tipo="Nível baixo",
            mensagem="Nível abaixo do esperado",
            status="Pendente",
            dataHora=timezone.now(),
        )
        abastecimento = Abastecimento.objects.create(
            usuario=self.usuario,
            cisterna=self.cisterna,
            dataHora=timezone.now(),
            quantidadeAgua=Decimal("20.00"),
            tipo="Caminhão-pipa",
            observacao="Reposição de água",
            status="Concluído",
        )

        self.client.post(reverse("usuario_excluir", args=[self.usuario.pk]))

        self.assertFalse(Usuario.objects.filter(pk=self.usuario.pk).exists())
        self.assertFalse(Cisterna.objects.filter(pk=self.cisterna.pk).exists())
        self.assertFalse(
            Monitoramento.objects.filter(pk=self.monitoramento.pk).exists()
        )
        self.assertFalse(Alerta.objects.filter(pk=alerta.pk).exists())
        self.assertFalse(
            Abastecimento.objects.filter(pk=abastecimento.pk).exists()
        )

    def test_monitoramento_e_abastecimento_rejeitam_responsavel_incompativel(self):
        outro_usuario = Usuario.objects.create_user(
            username="outro_usuario",
            email="outro@email.com",
            password="senha123",
            nome="Outro Usuario",
            cpf="52998224725",
        )
        data_hora = timezone.now().strftime("%Y-%m-%dT%H:%M")

        monitoramento_form = MonitoramentoForm(
            {
                "usuario": str(outro_usuario.pk),
                "cisterna": str(self.cisterna.pk),
                "dataHora": data_hora,
                "nivelAgua": "10.00",
                "consumo": "1.00",
                "situacao": "Leitura válida",
            }
        )
        self.assertFalse(monitoramento_form.is_valid())
        self.assertIn("cisterna", monitoramento_form.errors)

        abastecimento_form = AbastecimentoForm(
            {
                "usuario": str(outro_usuario.pk),
                "cisterna": str(self.cisterna.pk),
                "dataHora": data_hora,
                "quantidadeAgua": "10.00",
                "tipo": "Caminhão-pipa",
                "observacao": "Reposição válida",
                "status": "Concluído",
            }
        )
        self.assertFalse(abastecimento_form.is_valid())
        self.assertIn("cisterna", abastecimento_form.errors)

    def test_rotas_de_registros_inexistentes_retornam_404(self):
        rotas = (
            "usuario",
            "cisterna",
            "monitoramento",
            "alerta",
            "abastecimento",
        )
        operacoes = ("detalhar", "editar", "excluir")

        for entidade in rotas:
            for operacao in operacoes:
                with self.subTest(entidade=entidade, operacao=operacao):
                    response = self.client.get(
                        reverse(
                            f"{entidade}_{operacao}",
                            args=[999999],
                        )
                    )
                    self.assertEqual(response.status_code, 404)