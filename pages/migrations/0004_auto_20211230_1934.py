# Generated by Django 3.1.7 on 2021-12-30 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_auto_20211227_2237'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='type',
            new_name='name',
        ),
    ]