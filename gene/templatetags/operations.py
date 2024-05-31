from django import template
register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return value*arg
    except (ValueError, TypeError):
        return ''