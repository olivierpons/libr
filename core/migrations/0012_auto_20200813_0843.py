# Generated by Django 3.0.8 on 2020-08-13 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20200324_2100'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentfile',
            name='path_relative_to_media_root',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='imagefile',
            name='path_relative_to_media_root',
            field=models.BooleanField(default=True),
        ),
    ]
