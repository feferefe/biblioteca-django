from decimal import Decimal

from django.core.management.base import BaseCommand

from livraria.models import Autor, Categoria, Livro, Membro

CATEGORIAS = ["Romance", "Ficção Científica", "Fantasia", "Clássico", "Programação"]

AUTORES = {
    "Machado de Assis": "Brasileira",
    "George Orwell": "Britânica",
    "J.R.R. Tolkien": "Britânica",
    "J.K. Rowling": "Britânica",
    "Isaac Asimov": "Americana",
    "Robert C. Martin": "Americana",
    "Paulo Coelho": "Brasileira",
}

# titulo, autor, isbn, ano, exemplares, preco, categorias
LIVROS = [
    ("Dom Casmurro", "Machado de Assis", "9788535910663", 1899, 3, "39.90", ["Romance", "Clássico"]),
    ("Memórias Póstumas de Brás Cubas", "Machado de Assis", "9788535911664", 1881, 2, "42.00", ["Romance", "Clássico"]),
    ("1984", "George Orwell", "9788535914849", 1949, 3, "49.90", ["Ficção Científica"]),
    ("A Revolução dos Bichos", "George Orwell", "9788535909555", 1945, 2, "32.00", ["Clássico"]),
    ("O Hobbit", "J.R.R. Tolkien", "9788533613379", 1937, 2, "59.90", ["Fantasia"]),
    ("O Senhor dos Anéis", "J.R.R. Tolkien", "9788533613416", 1954, 1, "79.90", ["Fantasia"]),
    ("Harry Potter e a Pedra Filosofal", "J.K. Rowling", "9788532530787", 1997, 3, "54.90", ["Fantasia"]),
    ("Fundação", "Isaac Asimov", "9788576572008", 1951, 2, "52.00", ["Ficção Científica"]),
    ("Código Limpo", "Robert C. Martin", "9788576082675", 2008, 1, "89.90", ["Programação"]),
    ("O Alquimista", "Paulo Coelho", "9788576657804", 1988, 3, "34.90", ["Romance"]),
]

MEMBROS = [
    ("Ana Souza", "ana.souza@email.com"),
    ("Bruno Lima", "bruno.lima@email.com"),
    ("Carla Mendes", "carla.mendes@email.com"),
    ("Diego Alves", "diego.alves@email.com"),
]


class Command(BaseCommand):
    help = "Cadastra autores, categorias, livros e membros de exemplo (pode rodar mais de uma vez)."

    def handle(self, *args, **options):
        cats = {n: Categoria.objects.get_or_create(nome=n)[0] for n in CATEGORIAS}
        autores = {
            n: Autor.objects.get_or_create(nome=n, defaults={"nacionalidade": nac})[0]
            for n, nac in AUTORES.items()
        }
        novos = 0
        for titulo, autor, isbn, ano, qtd, preco, cs in LIVROS:
            livro, criado = Livro.objects.get_or_create(
                isbn=isbn,
                defaults={
                    "titulo": titulo,
                    "autor": autores[autor],
                    "ano_publicacao": ano,
                    "exemplares_disponiveis": qtd,
                    "preco": Decimal(preco),
                },
            )
            if criado:
                livro.categorias.set([cats[c] for c in cs])
                novos += 1
        for nome, email in MEMBROS:
            Membro.objects.get_or_create(email=email, defaults={"nome": nome})
        self.stdout.write(self.style.SUCCESS(
            f"Pronto: {novos} livros novos, {len(AUTORES)} autores, "
            f"{len(CATEGORIAS)} categorias e {len(MEMBROS)} membros."
        ))
