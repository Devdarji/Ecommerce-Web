from django.contrib import admin

from shop.models import Brand, Category, Item, Order, Profile, ShippingAddress

# Register your models here.
admin.site.register(ShippingAddress)
admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Brand)
admin.site.register(Order)
