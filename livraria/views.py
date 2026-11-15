from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import EmprestimoForm, LivroForm, MembroForm
from .models import Emprestimo, Livro, Membro


def home(request):
    ativos = Emprestimo.objects.filter(data_devolucao__isnull=True)
    contexto = {
        "total_livros": Livro.objects.count(),
        "total_membros": Membro.objects.count(),
        "emprestimos_ativos": ativos.count(),
        "emprestimos_atrasados": ativos.filter(data_prevista__lt=timezone.localdate()).count(),
        "ultimos_emprestimos": Emprestimo.objects.select_related("livro", "membro")[:5],
    }
    return render(request, "livraria/home.html", contexto)


# ---------- CRUD completo de Livro ----------
class LivroListView(ListView):  # Read: listar + busca
    model = Livro
    template_name = "livraria/livro_list.html"
    context_object_name = "livros"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset().select_related("autor")
        busca = self.request.GET.get("q", "").strip()
        if busca:
            qs = qs.filter(Q(titulo__icontains=busca) | Q(autor__nome__icontains=busca))
        return qs


class LivroDetailView(DetailView):  # Read: visualizar
    model = Livro
    template_name = "livraria/livro_detail.html"


class LivroCreateView(CreateView):  # Create
    model = Livro
    form_class = LivroForm
    template_name = "livraria/form.html"
    success_url = reverse_lazy("livraria:livro_list")
    extra_context = {"titulo": "Novo livro"}

    def form_valid(self, form):
        messages.success(self.request, "Livro cadastrado com sucesso!")
        return super().form_valid(form)


class LivroUpdateView(UpdateView):  # Update
    model = Livro
    form_class = LivroForm
    template_name = "livraria/form.html"
    success_url = reverse_lazy("livraria:livro_list")
    extra_context = {"titulo": "Editar livro"}

    def form_valid(self, form):
        messages.success(self.request, "Livro atualizado com sucesso!")
        return super().form_valid(form)


class LivroDeleteView(DeleteView):  # Delete
    model = Livro
    template_name = "livraria/livro_confirm_delete.html"
    success_url = reverse_lazy("livraria:livro_list")

    def form_valid(self, form):
        try:
            resposta = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, "Não é possível excluir: o livro possui empréstimos.")
            return redirect("livraria:livro_list")
        messages.success(self.request, "Livro excluído.")
        return resposta


# ---------- Membros ----------
class MembroListView(ListView):
    model = Membro
    template_name = "livraria/membro_list.html"
    context_object_name = "membros"


class MembroCreateView(CreateView):
    model = Membro
    form_class = MembroForm
    template_name = "livraria/form.html"
    success_url = reverse_lazy("livraria:membro_list")
    extra_context = {"titulo": "Novo membro"}

    def form_valid(self, form):
        messages.success(self.request, "Membro cadastrado!")
        return super().form_valid(form)


# ---------- Empréstimos (regras de negócio) ----------
def emprestimo_list(request):
    emprestimos = Emprestimo.objects.select_related("livro", "membro")
    return render(request, "livraria/emprestimo_list.html", {"emprestimos": emprestimos})


def emprestimo_create(request):
    form = EmprestimoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():  # validação (inclui Model.clean)
        form.save()  # processamento + persistência
        messages.success(request, "Empréstimo registrado! Prazo de 14 dias.")  # retorno
        return redirect("livraria:emprestimo_list")
    return render(request, "livraria/form.html", {"form": form, "titulo": "Novo empréstimo"})


@require_POST
def emprestimo_devolver(request, pk):
    emprestimo = get_object_or_404(Emprestimo, pk=pk)
    try:
        emprestimo.registrar_devolucao()
        messages.success(request, "Devolução registrada e estoque atualizado.")
    except ValidationError as erro:
        messages.error(request, erro.messages[0])
    return redirect("livraria:emprestimo_list")
