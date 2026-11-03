from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from alertas.models import Alerta
from cisternas.models import Cisterna
from usuarios.models import Usuario


class PermissoesPorDonoTests(TestCase):
    def setUp(self):
        self.ana = Usuario.objects.create_user(
            username="ana",
            email="ana@email.com",
            password="senha123",
            nome="Ana",
            cpf="12345678909",
        )
        self.bia = Usuario.objects.create_user(
            username="bia",
            email="bia@email.com",
            password="senha123",
            nome="Bia",
            cpf="52998224725",
        )
        self.admin = Usuario.objects.create_user(
            username="admin_teste",
            email="admin@email.com",
            password="senha123",
            nome="Admin",
            cpf="11144477735",
        )
        self.admin.is_staff = True
        self.admin.save(update_fields=("is_staff",))

        self.cisterna_ana = self._criar_cisterna(self.ana, "Cisterna da Ana")
        self.cisterna_bia = self._criar_cisterna(self.bia, "Cisterna da Bia")

    def _criar_cisterna(self, usuario, descricao):
        return Cisterna.objects.create(
            usuario=usuario,
            latitude=Decimal("-14.2230000"),
            longitude=Decimal("-42.7810000"),
            capacidade=Decimal("1000.00"),
            descricao=descricao,
            status="Ativa",
        )

    def _dados_cisterna(self, usuario, descricao):
        return {
            "usuario": str(usuario.pk),
            "latitude": "-14.2230000",
            "longitude": "-42.7810000",
            "capacidade": "900.00",
            "descricao": descricao,
            "status": "Ativa",
        }

    def test_usuario_comum_ve_apenas_as_proprias_cisternas(self):
        self.client.force_login(self.ana)

        resposta = self.client.get(reverse("cisterna_listar"))
        self.assertContains(resposta, "Cisterna da Ana")
        self.assertNotContains(resposta, "Cisterna da Bia")

        for operacao in ("detalhar", "editar", "excluir"):
            with self.subTest(operacao=operacao):
                resposta = self.client.get(
                    reverse(f"cisterna_{operacao}", args=[self.cisterna_bia.pk])
                )
                self.assertEqual(resposta.status_code, 404)

    def test_usuario_comum_cadastra_cisterna_sempre_no_proprio_nome(self):
        self.client.force_login(self.ana)

        resposta = self.client.post(
            reverse("cisterna_criar"),
            self._dados_cisterna(self.bia, "Cisterna nova"),
        )

        self.assertEqual(resposta.status_code, 302)
        nova = Cisterna.objects.get(descricao="Cisterna nova")
        self.assertEqual(nova.usuario_id, self.ana.pk)

    def test_cisterna_cadastrada_pelo_admin_pertence_ao_usuario_escolhido(self):
        self.client.force_login(self.admin)
        self.client.post(
            reverse("cisterna_criar"),
            self._dados_cisterna(self.bia, "Cisterna do admin para Bia"),
        )

        cisterna = Cisterna.objects.get(descricao="Cisterna do admin para Bia")
        self.assertEqual(cisterna.usuario_id, self.bia.pk)

        self.client.force_login(self.bia)
        resposta = self.client.get(reverse("cisterna_listar"))
        self.assertContains(resposta, "Cisterna do admin para Bia")
        self.assertEqual(
            self.client.get(
                reverse("cisterna_editar", args=[cisterna.pk])
            ).status_code,
            200,
        )

        resposta = self.client.post(
            reverse("cisterna_excluir", args=[cisterna.pk])
        )
        self.assertEqual(resposta.status_code, 302)
        self.assertFalse(Cisterna.objects.filter(pk=cisterna.pk).exists())

    def test_usuario_comum_nao_registra_nem_ve_dados_de_outra_cisterna(self):
        alerta_da_bia = Alerta.objects.create(
            cisterna=self.cisterna_bia,
            tipo="Nível baixo",
            mensagem="Alerta da cisterna da Bia",
            status="Pendente",
            dataHora=timezone.now(),
        )

        self.client.force_login(self.ana)

        resposta = self.client.get(
            reverse("alerta_detalhar", args=[alerta_da_bia.pk])
        )
        self.assertEqual(resposta.status_code, 404)

        resposta = self.client.post(
            reverse("alerta_criar"),
            {
                "cisterna": str(self.cisterna_bia.pk),
                "tipo": "Cheia",
                "mensagem": "Tentativa indevida",
                "status": "Pendente",
                "dataHora": timezone.now().strftime("%Y-%m-%dT%H:%M"),
            },
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(
            Alerta.objects.filter(mensagem="Tentativa indevida").exists()
        )