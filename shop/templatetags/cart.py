from django import template


register = template.Library()   # Decorater

@register.filter(name="is_in_cart")
def is_in_cart(item, cart):                       # cart ---> key, value pair in this product and qty
    keys = cart.keys()
    for id in keys:
        if int(id) == item.id:
            return True
    return False


@register.filter(name="cart_qty")
def cart_qty(item, cart):
    keys = cart.keys()
    for id in keys:
        if int(id) == item.id:
            return cart.get(id)
    return 0


@register.filter(name="item_total")
def item_total(item, cart):
    return item.price * cart_qty(item, cart) 


@register.filter(name="cart_total")
def cart_total(item, cart):
    sum = 0
    for i in item:
        sum += item_total(i, cart)
    return sum
