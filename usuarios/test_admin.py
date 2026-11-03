from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Usuario


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
            reverse("admin:usuarios_usuario_add"),
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
        url = reverse("admin:usuarios_usuario_change", args=[usuario.pk])

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
