# Generated by Django 3.0.3 on 2020-03-24 19:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20200324_2022'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entityphone',
            old_name='phone',
            new_name='text',
        ),
    ]