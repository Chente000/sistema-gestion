from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def sub(value, arg):
    """
    Resta el argumento (arg) del valor (value).
    Uso: {{ value|sub:arg }}
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return '' # Devuelve vacío o un valor predeterminado en caso de error