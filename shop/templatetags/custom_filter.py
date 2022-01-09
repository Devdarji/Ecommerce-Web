from django import template
register = template.Library()   # Decorater


@register.filter(name="currency")
def currency(number):
    return "₹"+str(number)
