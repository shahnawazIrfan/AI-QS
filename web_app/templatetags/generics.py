from django import template
from datetime import datetime
import base64

register = template.Library()

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0.0)

@register.filter
def add(value, arg):
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        return ''