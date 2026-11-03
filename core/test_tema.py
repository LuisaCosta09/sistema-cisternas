from django.test import TestCase
from django.urls import reverse


class TemaTests(TestCase):
    def test_sistema_abre_em_tema_claro_com_interruptor_de_tema(self):
        resposta = self.client.get(reverse("entrar"))

        self.assertContains(
            resposta,
            '<html lang="pt-br" data-bs-theme="light">',
        )
        self.assertContains(resposta, 'id="alternar-tema"')
        self.assertContains(resposta, 'role="switch"')