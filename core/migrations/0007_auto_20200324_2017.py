# Generated by Django 3.0.3 on 2020-03-24 19:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20200324_2013'),
    ]

    operations = [
        migrations.RenameField(
            model_name='activitytype',
            old_name='name',
            new_name='text',
        ),
    ]
