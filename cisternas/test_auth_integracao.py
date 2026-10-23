import re

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Abastecimento, Alerta, Cisterna, Monitoramento, Usuario


class AutenticacaoIntegracaoTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="pedro_integracao",
            email="pedro.integracao@example.com",
            password="Teste#Integracao2026!",
            nome="Pedro Integracao",
            cpf="52998224725",
        )

    def test_visitante_volta_a_rota_protegida_apos_login(self):
        rota_solicitada = reverse("alerta_listar")
        resposta = self.client.get(rota_solicitada)

        self.assertRedirects(
            resposta,
            f"{reverse('entrar')}?next={rota_solicitada}",
        )

        resposta_login = self.client.post(
            reverse("entrar"),
            {
                "username": "pedro_integracao",
                "password": "Teste#Integracao2026!",
                "next": rota_solicitada,
            },
        )

        self.assertRedirects(resposta_login, rota_solicitada)
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_rejeita_redirecionamento_para_site_externo(self):
        resposta = self.client.post(
            reverse("entrar"),
            {
                "username": "pedro_integracao",
                "password": "Teste#Integracao2026!",
                "next": "https://example.org/fora-do-sistema/",
            },
        )

        self.assertRedirects(resposta, reverse("cisterna_listar"))
        self.assertIn("_auth_user_id", self.client.session)

    def _cliente_autenticado_com_token_csrf(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.usuario)
        resposta = cliente.get(reverse("cisterna_listar"))
        correspondencia = re.search(
            r'name="csrfmiddlewaretoken" value="([^"]+)"',
            resposta.content.decode(),
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertIsNotNone(correspondencia)
        return cliente, correspondencia.group(1)

    def test_logout_sem_csrf_rejeita_post_e_mantem_sessao(self):
        cliente, _ = self._cliente_autenticado_com_token_csrf()
        usuario_id = cliente.session["_auth_user_id"]

        resposta = cliente.post(reverse("sair"))

        self.assertEqual(resposta.status_code, 403)
        self.assertEqual(cliente.session.get("_auth_user_id"), usuario_id)

    def test_logout_com_csrf_valido_encerra_sessao(self):
        cliente, csrf_token = self._cliente_autenticado_com_token_csrf()

        resposta = cliente.post(
            reverse("sair"),
            {"csrfmiddlewaretoken": csrf_token},
        )

        self.assertRedirects(resposta, reverse("entrar"))
        self.assertNotIn("_auth_user_id", cliente.session)

    def test_usuario_autenticado_e_redirecionado_ao_acessar_login(self):
        self.client.force_login(self.usuario)

        resposta = self.client.get(reverse("entrar"))

        self.assertRedirects(resposta, reverse("cisterna_listar"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_usuario_comum_ve_apenas_a_propria_conta(self):
        usuario_alvo = Usuario.objects.create_user(
            username="usuario_alvo",
            email="usuario.alvo@example.com",
            password="Outra#Senha2026!",
            nome="Usuario Alvo",
            cpf="11144477735",
        )
        self.client.force_login(self.usuario)

        resposta_lista = self.client.get(reverse("usuario_listar"))
        self.assertEqual(resposta_lista.status_code, 200)
        self.assertContains(resposta_lista, self.usuario.nome)
        self.assertNotContains(resposta_lista, usuario_alvo.nome)
        self.assertNotContains(resposta_lista, usuario_alvo.email)
        self.assertNotContains(resposta_lista, usuario_alvo.cpf)
        self.assertEqual(len(resposta_lista.context["usuarios"]), 1)

        self.assertEqual(
            self.client.get(
                reverse("usuario_detalhar", args=[self.usuario.pk])
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(
                reverse("usuario_editar", args=[self.usuario.pk])
            ).status_code,
            200,
        )
        resposta_confirmacao = self.client.get(
            reverse("usuario_excluir", args=[self.usuario.pk])
        )
        self.assertEqual(resposta_confirmacao.status_code, 200)
        self.assertContains(
            resposta_confirmacao,
            "Tem certeza de que deseja excluir sua conta?",
        )
        self.assertTrue(Usuario.objects.filter(pk=self.usuario.pk).exists())

        self.assertEqual(
            self.client.get(
                reverse("usuario_criar")
            ).status_code,
            403,
        )
        for operacao in ("detalhar", "editar", "excluir"):
            with self.subTest(operacao=operacao):
                resposta = self.client.get(
                    reverse(f"usuario_{operacao}", args=[usuario_alvo.pk])
                )
                self.assertEqual(resposta.status_code, 404)

        contagem_antes = Usuario.objects.count()
        self.assertEqual(
            self.client.post(reverse("usuario_criar"), {}).status_code,
            403,
        )
        self.assertEqual(
            self.client.post(
                reverse("usuario_editar", args=[usuario_alvo.pk]), {}
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(
                reverse("usuario_excluir", args=[usuario_alvo.pk])
            ).status_code,
            404,
        )
        self.assertEqual(Usuario.objects.count(), contagem_antes)
        self.assertTrue(Usuario.objects.filter(pk=usuario_alvo.pk).exists())

        cisterna_propria = Cisterna.objects.create(
            usuario=self.usuario,
            latitude="-12.3456789",
            longitude="-45.6789012",
            capacidade="500.00",
            descricao="Cisterna própria",
            status="Ativa",
        )
        monitoramento_proprio = Monitoramento.objects.create(
            usuario=self.usuario,
            cisterna=cisterna_propria,
            dataHora=timezone.now(),
            nivelAgua="10.00",
            consumo="1.00",
            situacao="Leitura da própria conta",
        )
        alerta_proprio = Alerta.objects.create(
            cisterna=cisterna_propria,
            tipo="Nível baixo",
            mensagem="Alerta da própria conta",
            status="Pendente",
            dataHora=timezone.now(),
        )
        abastecimento_proprio = Abastecimento.objects.create(
            usuario=self.usuario,
            cisterna=cisterna_propria,
            dataHora=timezone.now(),
            quantidadeAgua="20.00",
            tipo="Caminhão-pipa",
            observacao="Abastecimento próprio",
            status="Concluído",
        )

        resposta_exclusao = self.client.post(
            reverse("usuario_excluir", args=[self.usuario.pk])
        )
        self.assertRedirects(resposta_exclusao, reverse("entrar"))
        self.assertFalse(Usuario.objects.filter(pk=self.usuario.pk).exists())
        self.assertTrue(Usuario.objects.filter(pk=usuario_alvo.pk).exists())
        self.assertFalse(Cisterna.objects.filter(pk=cisterna_propria.pk).exists())
        self.assertFalse(
            Monitoramento.objects.filter(pk=monitoramento_proprio.pk).exists()
        )
        self.assertFalse(Alerta.objects.filter(pk=alerta_proprio.pk).exists())
        self.assertFalse(
            Abastecimento.objects.filter(pk=abastecimento_proprio.pk).exists()
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_usuario_nao_exclui_cisterna_com_registros_de_terceiros(self):
        outro_usuario = Usuario.objects.create_user(
            username="terceiro_monitoramento",
            email="terceiro.monitoramento@example.com",
            password="Outra#Senha2026!",
            nome="Terceiro Monitoramento",
            cpf="11144477735",
        )
        cisterna = Cisterna.objects.create(
            usuario=self.usuario,
            latitude="-12.3456789",
            longitude="-45.6789012",
            capacidade="500.00",
            descricao="Cisterna da conta",
            status="Ativa",
        )
        monitoramento = Monitoramento.objects.create(
            usuario=outro_usuario,
            cisterna=cisterna,
            dataHora=timezone.now(),
            nivelAgua="10.00",
            consumo="1.00",
            situacao="Registro legado inconsistente",
        )
        self.client.force_login(self.usuario)

        resposta = self.client.post(
            reverse("usuario_excluir", args=[self.usuario.pk])
        )

        self.assertRedirects(
            resposta,
            reverse("usuario_detalhar", args=[self.usuario.pk]),
        )
        self.assertTrue(Usuario.objects.filter(pk=self.usuario.pk).exists())
        self.assertTrue(Cisterna.objects.filter(pk=cisterna.pk).exists())
        self.assertTrue(
            Monitoramento.objects.filter(pk=monitoramento.pk).exists()
        )

    def test_usuario_staff_consegue_usar_crud_de_usuarios(self):
        self.usuario.is_staff = True
        self.usuario.save(update_fields=("is_staff",))
        self.client.force_login(self.usuario)

        self.assertEqual(
            self.client.get(reverse("usuario_listar")).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("usuario_criar")).status_code,
            200,
        )

        resposta = self.client.post(
            reverse("usuario_criar"),
            {
                "username": "usuario_criado_staff",
                "email": "criado.staff@example.com",
                "nome": "Usuario Criado",
                "cpf": "11144477735",
                "password1": "Crie#Conta2026Segura!",
                "password2": "Crie#Conta2026Segura!",
            },
        )
        self.assertRedirects(resposta, reverse("usuario_listar"))
        usuario_alvo = Usuario.objects.get(username="usuario_criado_staff")
        self.assertTrue(usuario_alvo.check_password("Crie#Conta2026Segura!"))

        self.assertEqual(
            self.client.get(
                reverse("usuario_detalhar", args=[usuario_alvo.pk])
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(
                reverse("usuario_editar", args=[usuario_alvo.pk])
            ).status_code,
            200,
        )
        resposta_edicao = self.client.post(
            reverse("usuario_editar", args=[usuario_alvo.pk]),
            {
                "username": "usuario_criado_staff",
                "email": "editado.staff@example.com",
                "nome": "Usuario Editado",
                "cpf": "11144477735",
            },
        )
        self.assertRedirects(
            resposta_edicao,
            reverse("usuario_detalhar", args=[usuario_alvo.pk]),
        )
        usuario_alvo.refresh_from_db()
        self.assertEqual(usuario_alvo.nome, "Usuario Editado")

        self.assertEqual(
            self.client.get(
                reverse("usuario_excluir", args=[usuario_alvo.pk])
            ).status_code,
            200,
        )
        resposta_exclusao = self.client.post(
            reverse("usuario_excluir", args=[usuario_alvo.pk]),
        )
        self.assertRedirects(resposta_exclusao, reverse("usuario_listar"))
        self.assertFalse(Usuario.objects.filter(pk=usuario_alvo.pk).exists())
