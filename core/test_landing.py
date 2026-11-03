from django.test import TestCase
from django.urls import reverse


class PaginaInicialTests(TestCase):
    def test_visitante_acessa_a_pagina_inicial(self):
        resposta = self.client.get(reverse("landing"))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Sistema de Cisternas")
        self.assertContains(resposta, "TemplateMo")