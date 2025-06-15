from django import template
from datetime import datetime
import base64

register = template.Library()

@register.filter
def subtract(value, arg):
    return value - arg