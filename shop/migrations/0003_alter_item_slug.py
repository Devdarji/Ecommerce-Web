# Generated by Django 4.0 on 2022-01-05 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_category_item'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='slug',
            field=models.SlugField(blank=True),
        ),
    ]
