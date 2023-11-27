# Generated by Django 3.2.3 on 2023-11-27 13:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_ingredients_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tags',
            name='slug',
            field=models.SlugField(max_length=200, null=True, unique=True, validators=[django.core.validators.RegexValidator('^[-a-zA-Z0-9_]+$')]),
        ),
    ]
