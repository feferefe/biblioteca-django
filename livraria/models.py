from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

PRAZO_EMPRESTIMO_DIAS = 14
LIMITE_EMPRESTIMOS_ATIVOS = 3


class Autor(models.Model):
    nome = models.CharField(max_length=120)
    nacionalidade = models.CharField(max_length=60, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["nome"]
        verbose_name_plural = "autores"

    def __str__(self):
        return self.nome


class Categoria(models.Model):
    nome = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    isbn = models.CharField("ISBN", max_length=13, unique=True)
    ano_publicacao = models.PositiveIntegerField()
    exemplares_disponiveis = models.PositiveIntegerField(default=1)
    preco = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    sinopse = models.TextField(blank=True)
    autor = models.ForeignKey(Autor, on_delete=models.PROTECT, related_name="livros")
    categorias = models.ManyToManyField(Categoria, related_name="livros", blank=True)

    class Meta:
        ordering = ["titulo"]

    def __str__(self):
        return f"{self.titulo} ({self.autor})"


class Membro(models.Model):
    nome = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    data_cadastro = models.DateField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome

    def emprestimos_ativos(self):
        return self.emprestimos.filter(data_devolucao__isnull=True)


class Emprestimo(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.PROTECT, related_name="emprestimos")
    membro = models.ForeignKey(Membro, on_delete=models.PROTECT, related_name="emprestimos")
    data_emprestimo = models.DateField(default=timezone.localdate)
    data_prevista = models.DateField(blank=True)
    data_devolucao = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-data_emprestimo"]

    def __str__(self):
        return f"{self.livro.titulo} -> {self.membro.nome}"

    @property
    def devolvido(self):
        return self.data_devolucao is not None

    @property
    def atrasado(self):
        return not self.devolvido and self.data_prevista < timezone.localdate()

    def clean(self):
        """Regras de negócio aplicadas no servidor (valem no site e no Admin)."""
        if self.pk or not self.livro_id or not self.membro_id:
            return  # regras valem apenas para NOVOS empréstimos

        # Regra 1: membro inativo não pode pegar livros.
        if not self.membro.ativo:
            raise ValidationError("Membro inativo não pode realizar empréstimos.")

        # Regra 2: só empresta se houver exemplar disponível.
        estoque = Livro.objects.filter(pk=self.livro_id).values_list(
            "exemplares_disponiveis", flat=True
        ).first()
        if not estoque or estoque < 1:
            raise ValidationError("Não há exemplares disponíveis deste livro.")

        # Regra 3: limite de empréstimos ativos por membro.
        if self.membro.emprestimos_ativos().count() >= LIMITE_EMPRESTIMOS_ATIVOS:
            raise ValidationError(
                f"O membro já possui {LIMITE_EMPRESTIMOS_ATIVOS} empréstimos ativos."
            )

        # Regra 4: membro com livro em atraso fica bloqueado.
        hoje = timezone.localdate()
        if self.membro.emprestimos_ativos().filter(data_prevista__lt=hoje).exists():
            raise ValidationError("Membro possui empréstimo em atraso e está bloqueado.")

    def save(self, *args, **kwargs):
        novo = self.pk is None
        if novo:
            self.full_clean(exclude=["data_prevista"])
            if not self.data_prevista:
                self.data_prevista = self.data_emprestimo + timedelta(days=PRAZO_EMPRESTIMO_DIAS)
        super().save(*args, **kwargs)
        if novo:
            # Regra 5: baixa automática no estoque ao emprestar.
            Livro.objects.filter(pk=self.livro_id).update(
                exemplares_disponiveis=models.F("exemplares_disponiveis") - 1
            )

    def registrar_devolucao(self):
        """Regra 6: devolver repõe o exemplar no estoque (apenas uma vez)."""
        if self.devolvido:
            raise ValidationError("Este empréstimo já foi devolvido.")
        self.data_devolucao = timezone.localdate()
        super().save(update_fields=["data_devolucao"])
        Livro.objects.filter(pk=self.livro_id).update(
            exemplares_disponiveis=models.F("exemplares_disponiveis") + 1
        )

    def delete(self, *args, **kwargs):
        if not self.devolvido:
            Livro.objects.filter(pk=self.livro_id).update(
                exemplares_disponiveis=models.F("exemplares_disponiveis") + 1
            )
        return super().delete(*args, **kwargs)
