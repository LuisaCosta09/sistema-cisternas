import re

from django.test import Client, TestCase
from django.urls import reverse

from .models import Usuario


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
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertRedirects(resposta, reverse("entrar"))
        self.assertNotIn("_auth_user_id", cliente.session)

    def test_usuario_autenticado_e_redirecionado_ao_acessar_login(self):
        self.client.force_login(self.usuario)

        resposta = self.client.get(reverse("entrar"))

        self.assertRedirects(resposta, reverse("cisterna_listar"))
        self.assertIn("_auth_user_id", self.client.session)
