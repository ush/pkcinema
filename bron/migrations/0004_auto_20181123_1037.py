# Generated by Django 2.1.2 on 2018-11-23 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bron', '0003_booking_mero'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='places',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
