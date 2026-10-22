
from django.test import TestCase
from django.urls import reverse

from .models import Usuario


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="teste_login",
            email="teste_login@example.com",
            password="Senha#Forte2026!",
            nome="Teste Login",
            cpf="52998224725",
        )

    def test_login_e_publico(self):
        resposta = self.client.get(reverse("entrar"))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Entrar no sistema")

    def test_login_com_senha_correta(self):
        resposta = self.client.post(
            reverse("entrar"),
            {
                "username": "teste_login",
                "password": "Senha#Forte2026!",
            },
        )

        self.assertRedirects(
            resposta,
            reverse("cisterna_listar"),
        )
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_com_senha_incorreta(self):
        resposta = self.client.post(
            reverse("entrar"),
            {
                "username": "teste_login",
                "password": "senha_errada",
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertTrue(resposta.context["form"].errors)

    def test_logout_exige_post_e_limpa_sessao(self):
        self.client.force_login(self.usuario)

        resposta_get = self.client.get(reverse("sair"))

        self.assertEqual(resposta_get.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

        resposta_post = self.client.post(reverse("sair"))

        self.assertRedirects(
            resposta_post,
            reverse("entrar"),
        )
        self.assertNotIn("_auth_user_id", self.client.session)
