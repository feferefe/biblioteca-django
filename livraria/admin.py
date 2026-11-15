from django.contrib import admin

from .models import Autor, Categoria, Emprestimo, Livro, Membro

admin.site.site_header = "Administração da Biblioteca"
admin.site.site_title = "Biblioteca"
admin.site.index_title = "Gerenciar acervo e empréstimos"


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ("nome", "nacionalidade", "data_nascimento")
    search_fields = ("nome",)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "isbn", "ano_publicacao", "exemplares_disponiveis", "preco")
    list_filter = ("autor", "categorias", "ano_publicacao")
    search_fields = ("titulo", "isbn", "autor__nome")
    filter_horizontal = ("categorias",)


@admin.register(Membro)
class MembroAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "ativo", "data_cadastro")
    list_filter = ("ativo",)
    search_fields = ("nome", "email")


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ("livro", "membro", "data_emprestimo", "data_prevista", "data_devolucao")
    list_filter = ("data_emprestimo", "data_devolucao")
    search_fields = ("livro__titulo", "membro__nome")
    date_hierarchy = "data_emprestimo"
