
from django.test import TestCase
from django.urls import reverse

from .models import Usuario


class RotasProtegidasTests(TestCase):
    ROTAS_SEM_PK = (
        "inicio",
        "usuario_listar", "usuario_criar",
        "cisterna_listar", "cisterna_criar",
        "monitoramento_listar", "monitoramento_criar",
        "alerta_listar", "alerta_criar",
        "abastecimento_listar", "abastecimento_criar",
    )

    ROTAS_COM_PK = tuple(
        f"{entidade}_{operacao}"
        for entidade in (
            "usuario", "cisterna", "monitoramento",
            "alerta", "abastecimento",
        )
        for operacao in ("detalhar", "editar", "excluir")
    )

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="teste_rotas",
            email="teste_rotas@example.com",
            password="Senha#Forte2026!",
            nome="Teste Rotas",
            cpf="52998224725",
        )

    def test_visitante_e_redirecionado_ao_login(self):
        for nome in self.ROTAS_SEM_PK:
            with self.subTest(nome=nome):
                endereco = reverse(nome)
                resposta = self.client.get(endereco)
                self.assertRedirects(
                    resposta,
                    f"{reverse('entrar')}?next={endereco}",
                )

        for nome in self.ROTAS_COM_PK:
            with self.subTest(nome=nome):
                endereco = reverse(nome, args=[999999])
                resposta = self.client.get(endereco)
                self.assertRedirects(
                    resposta,
                    f"{reverse('entrar')}?next={endereco}",
                )

    def test_usuario_logado_acessa_paginas_sem_pk(self):
        self.client.force_login(self.usuario)

        for nome in self.ROTAS_SEM_PK:
            with self.subTest(nome=nome):
                resposta = self.client.get(reverse(nome))

                if nome == "inicio":
                    self.assertRedirects(
                        resposta,
                        reverse("cisterna_listar"),
                    )
                else:
                    self.assertEqual(resposta.status_code, 200)

    def test_usuario_logado_recebe_404_para_pk_inexistente(self):
        self.client.force_login(self.usuario)

        for nome in self.ROTAS_COM_PK:
            with self.subTest(nome=nome):
                resposta = self.client.get(
                    reverse(nome, args=[999999])
                )
                self.assertEqual(resposta.status_code, 404)
