from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import datetime
# Create your models here.

class ShippingAddress(models.Model):
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    zipcode = models.IntegerField(max_length=10)
    country = models.CharField(max_length=20)

    def __str__(self):
        return self.address_line1 + ' ' + self.address_line2

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField()
    mobile_no = models.IntegerField(max_length=12)
    alternate_mobile_no = models.IntegerField(max_length=12)
    address = models.ManyToManyField(ShippingAddress)


    def __str__(self):
        return self.user.username

class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='images/category')

    def __str__(self):
        return self.title

class Brand(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    slug = models.SlugField(blank=True)
    stock= models.CharField(max_length=10)
    description = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/item')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_cat_list(self):
        k = self.category  

        breadcrumb = ["dummy"]
        while k is not None:
            breadcrumb.append(k.slug)
            k = k.parent
        for i in range(len(breadcrumb) - 1):
            breadcrumb[i] = '/'.join(breadcrumb[-1:i - 1:-1])
        return breadcrumb[-1:0:-1]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Item, self).save(*args, **kwargs)


    def get_items_by_id(ids):
        return Item.objects.filter(id__in= ids)

# class CartItem(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     ordered = models.BooleanField(default=False)
#     item = models.ForeignKey(Item, on_delete=models.CASCADE)
#     qty = models.PositiveIntegerField(default=0)

#     def __str__(self) -> str:
#         return str(self.cart) + ' ' + str(self.item)

class Order(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    qty = models.IntegerField(default=1)
    price = models.IntegerField()
    date = models.DateField(default=datetime.datetime.today)

    def __str__(self) -> str:
        return self.item.title