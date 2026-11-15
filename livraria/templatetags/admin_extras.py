from django import template
from django.apps import apps

register = template.Library()


@register.simple_tag
def contagem(app_label, nome_modelo):
    """Quantidade de registros de um modelo (usada nos cartões da página inicial do Admin)."""
    try:
        return apps.get_model(app_label, nome_modelo).objects.count()
    except LookupError:
        return "-"
