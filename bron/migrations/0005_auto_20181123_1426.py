# Generated by Django 2.1.2 on 2018-11-23 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bron', '0004_auto_20181123_1037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='places',
            field=models.CharField(max_length=30),
        ),
    ]
