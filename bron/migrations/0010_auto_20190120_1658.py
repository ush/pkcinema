# Generated by Django 2.1.2 on 2019-01-20 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bron', '0009_auto_20190119_2233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='merop',
            name='id',
        ),
        migrations.AddField(
            model_name='merop',
            name='prikol',
            field=models.CharField(default=1, max_length=30),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='merop',
            name='mero',
            field=models.CharField(max_length=30, primary_key=True, serialize=False),
        ),
    ]
