# Generated by Django 5.0.8 on 2024-08-31 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_room_creator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]