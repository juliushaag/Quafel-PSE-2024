# Generated by Django 5.0.6 on 2024-07-16 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulation_data', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simulationrun',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
