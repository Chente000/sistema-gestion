# dict_extras.py
from django import template
register = template.Library()

@register.simple_tag
def get_dict_item(dict_data, key):
    return dict_data.get(key)