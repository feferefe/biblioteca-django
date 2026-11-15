from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Autor, Emprestimo, Livro, Membro


class RegrasDeNegocioTests(TestCase):
    def setUp(self):
        autor = Autor.objects.create(nome="Machado de Assis")
        self.livro = Livro.objects.create(
            titulo="Dom Casmurro", isbn="9788535910663", ano_publicacao=1899,
            exemplares_disponiveis=1, autor=autor,
        )
        self.membro = Membro.objects.create(nome="Ana", email="ana@x.com")

    def test_emprestimo_baixa_estoque(self):
        Emprestimo.objects.create(livro=self.livro, membro=self.membro)
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.exemplares_disponiveis, 0)

    def test_sem_estoque_bloqueia(self):
        Emprestimo.objects.create(livro=self.livro, membro=self.membro)
        outro = Membro.objects.create(nome="Bia", email="bia@x.com")
        with self.assertRaises(ValidationError):
            Emprestimo.objects.create(livro=self.livro, membro=outro)

    def test_devolucao_repoe_estoque(self):
        e = Emprestimo.objects.create(livro=self.livro, membro=self.membro)
        e.registrar_devolucao()
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.exemplares_disponiveis, 1)
        with self.assertRaises(ValidationError):
            e.registrar_devolucao()

    def test_membro_inativo_bloqueado(self):
        self.membro.ativo = False
        self.membro.save()
        with self.assertRaises(ValidationError):
            Emprestimo.objects.create(livro=self.livro, membro=self.membro)

    def test_limite_de_tres_emprestimos(self):
        for i in range(3):
            l = Livro.objects.create(titulo=f"L{i}", isbn=f"123456789{i}", ano_publicacao=2000,
                                     exemplares_disponiveis=2, autor=self.livro.autor)
            Emprestimo.objects.create(livro=l, membro=self.membro)
        with self.assertRaises(ValidationError):
            Emprestimo.objects.create(livro=self.livro, membro=self.membro)

    def test_atraso_bloqueia_novo_emprestimo(self):
        velho = timezone.localdate() - timedelta(days=30)
        l2 = Livro.objects.create(titulo="Velho", isbn="1234567899", ano_publicacao=2000,
                                  exemplares_disponiveis=1, autor=self.livro.autor)
        Emprestimo.objects.create(livro=l2, membro=self.membro, data_emprestimo=velho)
        with self.assertRaises(ValidationError):
            Emprestimo.objects.create(livro=self.livro, membro=self.membro)


class FluxoWebTests(TestCase):
    def test_crud_livro_e_emprestimo(self):
        autor = Autor.objects.create(nome="Autor")
        r = self.client.post(reverse("livraria:livro_create"), {
            "titulo": "Novo", "isbn": "9788535910663", "ano_publicacao": 2020,
            "exemplares_disponiveis": 2, "preco": "10.00", "autor": autor.pk,
        })
        self.assertEqual(r.status_code, 302)
        livro = Livro.objects.get()
        membro = Membro.objects.create(nome="Ana", email="a@x.com")
        r = self.client.post(reverse("livraria:emprestimo_create"), {
            "livro": livro.pk, "membro": membro.pk, "data_emprestimo": timezone.localdate().isoformat(),
        })
        self.assertEqual(r.status_code, 302)
        livro.refresh_from_db()
        self.assertEqual(livro.exemplares_disponiveis, 1)
        for nome in ("home", "livro_list", "membro_list", "emprestimo_list"):
            self.assertEqual(self.client.get(reverse(f"livraria:{nome}")).status_code, 200)
        self.client.post(reverse("livraria:livro_update", args=[livro.pk]), {
            "titulo": "Editado", "isbn": "9788535910663", "ano_publicacao": 2020,
            "exemplares_disponiveis": 1, "preco": "10.00", "autor": autor.pk,
        })
        livro.refresh_from_db()
        self.assertEqual(livro.titulo, "Editado")
        Emprestimo.objects.all().delete()
        self.client.post(reverse("livraria:livro_delete", args=[livro.pk]))
        self.assertEqual(Livro.objects.count(), 0)
