# Generated by Django 2.1.2 on 2018-12-12 07:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bron', '0005_auto_20181123_1426'),
    ]

    operations = [
        migrations.CreateModel(
            name='Merop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mero', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.AlterField(
            model_name='booking',
            name='mero',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bron.Merop'),
        ),
    ]
