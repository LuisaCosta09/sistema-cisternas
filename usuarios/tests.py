from django.test import TestCase
from django.urls import reverse

from .models import Usuario


class UsuarioCrudTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="pedro",
            email="pedro@email.com",
            password="senha123",
            nome="Pedro",
            cpf="12345678909",
        )

        self.client.force_login(self.usuario)

    def test_usuario_crud_completo(self):
        self.usuario.is_staff = True
        self.usuario.save(update_fields=("is_staff",))

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