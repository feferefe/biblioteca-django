from django import forms

from .models import Emprestimo, Livro, Membro


class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = [
            "titulo", "isbn", "ano_publicacao", "exemplares_disponiveis",
            "preco", "sinopse", "autor", "categorias",
        ]
        widgets = {
            "categorias": forms.CheckboxSelectMultiple,
            "sinopse": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_isbn(self):
        isbn = self.cleaned_data["isbn"].replace("-", "").strip()
        if not isbn.isdigit() or len(isbn) not in (10, 13):
            raise forms.ValidationError("O ISBN deve ter 10 ou 13 dígitos numéricos.")
        return isbn


class MembroForm(forms.ModelForm):
    class Meta:
        model = Membro
        fields = ["nome", "email", "ativo"]


class EmprestimoForm(forms.ModelForm):
    """Fluxo: formulário -> validação (regras de negócio) -> persistência -> retorno."""

    class Meta:
        model = Emprestimo
        fields = ["livro", "membro", "data_emprestimo"]
        widgets = {"data_emprestimo": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Regras de negócio refletidas na interface: só livros com estoque e membros ativos.
        self.fields["livro"].queryset = Livro.objects.filter(exemplares_disponiveis__gt=0)
        self.fields["membro"].queryset = Membro.objects.filter(ativo=True)
