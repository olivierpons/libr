# Generated by Django 3.0.3 on 2020-03-24 19:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20200324_2012'),
    ]

    operations = [
        migrations.RenameField(
            model_name='phone',
            old_name='phone_number',
            new_name='text',
        ),
    ]