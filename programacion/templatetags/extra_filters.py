from django import template
register = template.Library()

@register.simple_tag
def get_item(grilla, aula_id, dia, hora):
    return grilla.get((aula_id, dia, hora))