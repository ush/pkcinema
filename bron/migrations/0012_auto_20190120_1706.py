# Generated by Django 2.1.2 on 2019-01-20 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bron', '0011_auto_20190120_1703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='mero',
            field=models.CharField(max_length=30),
        ),
    ]