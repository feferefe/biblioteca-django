from django.urls import path

from . import views

app_name = "livraria"

urlpatterns = [
    path("", views.home, name="home"),
    path("livros/", views.LivroListView.as_view(), name="livro_list"),
    path("livros/novo/", views.LivroCreateView.as_view(), name="livro_create"),
    path("livros/<int:pk>/", views.LivroDetailView.as_view(), name="livro_detail"),
    path("livros/<int:pk>/editar/", views.LivroUpdateView.as_view(), name="livro_update"),
    path("livros/<int:pk>/excluir/", views.LivroDeleteView.as_view(), name="livro_delete"),
    path("membros/", views.MembroListView.as_view(), name="membro_list"),
    path("membros/novo/", views.MembroCreateView.as_view(), name="membro_create"),
    path("emprestimos/", views.emprestimo_list, name="emprestimo_list"),
    path("emprestimos/novo/", views.emprestimo_create, name="emprestimo_create"),
    path("emprestimos/<int:pk>/devolver/", views.emprestimo_devolver, name="emprestimo_devolver"),
]
