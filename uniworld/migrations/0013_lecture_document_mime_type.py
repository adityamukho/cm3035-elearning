# Generated by Django 5.0.8 on 2024-09-06 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uniworld', '0012_assignmentsubmission_feedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecture',
            name='document_mime_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
