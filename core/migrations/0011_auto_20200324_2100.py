# Generated by Django 3.0.3 on 2020-03-24 20:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20200324_2049'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entityphone',
            old_name='text',
            new_name='phone',
        ),
    ]