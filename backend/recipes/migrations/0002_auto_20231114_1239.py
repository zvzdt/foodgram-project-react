# Generated by Django 3.2.3 on 2023-11-14 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='quantity',
            field=models.FloatField(verbose_name='количество'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='title',
            field=models.CharField(max_length=50, verbose_name='ингредиенты'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='units',
            field=models.CharField(max_length=10, verbose_name='единица измерения'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.DurationField(verbose_name='время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='description',
            field=models.TextField(verbose_name='описание'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to=None, verbose_name='фото'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='title',
            field=models.CharField(max_length=50, verbose_name='название'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=50, unique=True, verbose_name='цвет'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(unique=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='title',
            field=models.CharField(max_length=50, unique=True, verbose_name='имя тэга'),
        ),
    ]
