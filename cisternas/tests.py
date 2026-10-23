from decimal import Decimal

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import AbastecimentoForm, MonitoramentoForm
from .models import Abastecimento, Alerta, Cisterna, Monitoramento, Usuario


class CisternaMonitoramentoCrudTests(TestCase):
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

    def test_cisterna_permite_trocar_responsavel_sem_registros_dependentes(self):
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
        from .models import Abastecimento

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
            reverse("monitoramento_editar", args=[monitoramento.pk])
        )
        self.assertContains(response, "Editar monitoramento")
        self.assertContains(response, "Salvar alterações")

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

    def test_monitoramento_lista_estado_vazio(self):
        self.monitoramento.delete()

        response = self.client.get(reverse("monitoramento_listar"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nenhum monitoramento cadastrado")

    def test_usuario_crud_completo(self):
        response = self.client.get(reverse("usuario_listar"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuários cadastrados")

        response = self.client.get(reverse("usuario_criar"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("usuario_criar"),
            {
                "username": "usuario_novo",
                "email": "novo@email.com",
                "nome": "Usuario Novo",
                "cpf": "52998224725",
                "password1": "Agua#2026Seguro!x",
                "password2": "Agua#2026Seguro!x",
            },
        )
        self.assertEqual(response.status_code, 302)
        usuario = Usuario.objects.get(username="usuario_novo")
        self.assertTrue(usuario.check_password("Agua#2026Seguro!x"))

        response = self.client.get(
            reverse("usuario_editar", args=[usuario.pk])
        )
        self.assertContains(response, "Editar usuário")
        self.assertContains(response, "Salvar alterações")

        response = self.client.get(
            reverse("usuario_detalhar", args=[usuario.pk])
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("usuario_editar", args=[usuario.pk]),
            {
                "username": "usuario_novo",
                "email": "atualizado@email.com",
                "nome": "Usuario Atualizado",
                "cpf": "52998224725",
            },
        )
        self.assertEqual(response.status_code, 302)
        usuario.refresh_from_db()
        self.assertEqual(usuario.nome, "Usuario Atualizado")
        self.assertTrue(usuario.check_password("Agua#2026Seguro!x"))

        response = self.client.get(
            reverse("usuario_excluir", args=[usuario.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "abastecimentos")
        self.assertContains(response, "alertas")

        response = self.client.post(
            reverse("usuario_excluir", args=[usuario.pk]),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Usuario.objects.filter(pk=usuario.pk).exists())

    def test_alerta_e_abastecimento_crud_completo(self):
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
                "tipo": "Nível crítico",
                "mensagem": "Nível muito abaixo do esperado",
                "status": "Em análise",
                "dataHora": alerta_data,
            },
        )
        self.assertEqual(response.status_code, 302)
        alerta.refresh_from_db()
        self.assertEqual(alerta.tipo, "Nível crítico")
        self.assertEqual(
            self.client.get(
                reverse("alerta_excluir", args=[alerta.pk])
            ).status_code,
            200,
        )
        self.client.post(reverse("alerta_excluir", args=[alerta.pk]))
        self.assertFalse(Alerta.objects.filter(pk=alerta.pk).exists())

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

    def test_exclusao_de_usuario_remove_todos_os_dependentes_em_cascata(self):
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


class UsuarioAdminTests(TestCase):
    def setUp(self):
        admin_user = User.objects.create_superuser(
            username="administrador",
            email="admin@example.com",
            password="Admin#Password2026!",
        )
        self.client.force_login(admin_user)

    def test_admin_cria_usuario_com_senha_hash_e_credenciais_validas(self):
        response = self.client.post(
            reverse("admin:cisternas_usuario_add"),
            {
                "username": "admin_cadastrado",
                "nome": "Usuario do Admin",
                "cpf": "52998224725",
                "email": "admin-cadastrado@example.com",
                "password1": "R3de!Cisternas#2026",
                "password2": "R3de!Cisternas#2026",
                "_save": "Salvar",
            },
        )

        self.assertEqual(response.status_code, 302)
        usuario = Usuario.objects.get(username="admin_cadastrado")
        self.assertNotEqual(usuario.password, "R3de!Cisternas#2026")
        self.assertTrue(usuario.check_password("R3de!Cisternas#2026"))
        self.assertIsNotNone(
            authenticate(
                username="admin_cadastrado",
                password="R3de!Cisternas#2026",
            )
        )

    def test_admin_edita_usuario_sem_expor_ou_substituir_senha(self):
        usuario = Usuario.objects.create_user(
            username="usuario_admin",
            email="usuario-admin@example.com",
            password="R3de!Cisternas#2026",
            nome="Usuario Admin",
            cpf="52998224725",
        )
        senha_hash = usuario.password
        url = reverse("admin:cisternas_usuario_change", args=[usuario.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "R3de!Cisternas#2026")

        response = self.client.post(
            url,
            {
                "username": "usuario_admin",
                "nome": "Usuario Editado",
                "cpf": "52998224725",
                "email": "usuario-admin@example.com",
                "is_active": "on",
                "_save": "Salvar",
            },
        )

        self.assertEqual(response.status_code, 302)
        usuario.refresh_from_db()
        self.assertEqual(usuario.nome, "Usuario Editado")
        self.assertEqual(usuario.password, senha_hash)
        self.assertTrue(usuario.check_password("R3de!Cisternas#2026"))
