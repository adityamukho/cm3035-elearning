# Generated by Django 5.0.7 on 2024-08-09 03:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uniworld', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='description',
            field=models.TextField(default='Django Tutorials'),
            preserve_default=False,
        ),
    ]