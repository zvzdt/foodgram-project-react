# Generated by Django 3.2.3 on 2023-12-09 06:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20231205_1243'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipeingredients',
            old_name='ingredients',
            new_name='ingredient',
        ),
    ]