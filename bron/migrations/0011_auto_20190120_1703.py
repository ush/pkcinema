# Generated by Django 2.1.2 on 2019-01-20 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bron', '0010_auto_20190120_1658'),
    ]

    operations = [
        migrations.AddField(
            model_name='merop',
            name='id',
            field=models.AutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='merop',
            name='mero',
            field=models.CharField(max_length=30),
        ),
    ]
