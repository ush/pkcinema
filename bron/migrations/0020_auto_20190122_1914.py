# Generated by Django 2.1.2 on 2019-01-22 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bron', '0019_auto_20190122_1908'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='merop',
            name='prikol',
        ),
        migrations.AddField(
            model_name='merop',
            name='date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='merop',
            name='place',
            field=models.CharField(default='ur mom gay)))', max_length=30),
        ),
    ]