# Sistema de Biblioteca

## 1. Identificação

- **Nome da aplicação:** Sistema de Biblioteca (Django)
- **Nome do aluno:** Fernanda Rodrigues da Silva
- **Disciplina:** Técnicas Avançadas de Programação Web — Prof. Renato Sousa Botacim
- **Descrição resumida:** aplicação web em Django para cadastro de livros, autores, categorias e membros, com controle de empréstimos e devoluções.

## 2. Sobre o projeto

### a. Qual problema a aplicação resolve
Bibliotecas pequenas costumam controlar empréstimos em papel ou planilhas, o que gera erros: livros emprestados sem exemplar disponível, estoque desatualizado e membros que acumulam livros em atraso.

### b. Objetivo do sistema
Centralizar o acervo e os empréstimos, aplicando automaticamente as regras da biblioteca e mantendo o estoque sempre correto.

### c. Principais funcionalidades
- CRUD completo de **Livros** (listar com busca e paginação, visualizar, cadastrar, editar, excluir).
- Cadastro e listagem de **Membros**.
- Registro de **Empréstimos** e **Devoluções**.
- Painel inicial com totais.
- **Django Admin** com todos os modelos, `list_display`, filtros e busca, com visual personalizado no mesmo estilo do site.

### d. Regras de negócio implementadas (lado do servidor)
Estão em `livraria/models.py` (`Emprestimo.clean`, `save` e `registrar_devolucao`), portanto valem no site e no Admin.
1. **Sem estoque, sem empréstimo:** não é possível emprestar um livro sem exemplares disponíveis.
2. **Baixa automática de estoque:** ao registrar um empréstimo, o exemplar é descontado; ao devolver, é reposto (e uma devolução não pode ser feita duas vezes).
3. **Limite de 3 empréstimos ativos** por membro.
4. **Membro com livro em atraso é bloqueado** para novos empréstimos.
5. **Membro inativo** não pode pegar livros.
6. **Prazo automático:** a data prevista de devolução é calculada em 14 dias.

## 3. Tecnologias e bibliotecas
Python 3, Django 5.2 e SQLite (via Django ORM). Nenhuma biblioteca externa além do Django (ver `requirements.txt`).

## 4. Estrutura
```
biblioteca/
├── config/                    # configurações e urls do projeto
├── livraria/                  # app principal
│   ├── models.py  forms.py  views.py  urls.py  admin.py  tests.py
│   ├── migrations/
│   ├── management/commands/popular.py   # cadastra dados de exemplo
│   ├── templatetags/admin_extras.py     # contagem nos cartões do Admin
│   ├── templates/livraria/    # base.html + páginas (herança de templates)
│   ├── templates/admin/       # personalização visual do Django Admin
│   └── static/livraria/       # style.css (site) e admin.css (Admin)
├── manage.py
└── requirements.txt
```

## 5. Como executar
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # para acessar /admin/
python manage.py popular           # (opcional) cadastra livros, autores e membros de exemplo
python manage.py runserver
```
Acesse http://127.0.0.1:8000/ e o Admin em http://127.0.0.1:8000/admin/.

Testes automatizados: `python manage.py test`
