# Generated by Django 3.0.1 on 2019-12-28 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20191228_1207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentfile',
            name='informations',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='imagefile',
            name='informations',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]