# Generated by Django 5.0.8 on 2024-09-05 08:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uniworld', '0009_feedback'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('lecture', 'Lecture'), ('assignment', 'Assignment')], max_length=10)),
                ('sequence', models.IntegerField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='materials', to='uniworld.course')),
            ],
            options={
                'ordering': ['sequence'],
            },
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('material', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='uniworld.coursematerial')),
                ('due_date', models.DateTimeField()),
                ('questions', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Lecture',
            fields=[
                ('material', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='uniworld.coursematerial')),
                ('content', models.TextField()),
                ('video_url', models.URLField(blank=True, null=True)),
                ('document', models.FileField(blank=True, null=True, upload_to='lectures/')),
            ],
        ),
        migrations.CreateModel(
            name='AssignmentSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission', models.TextField()),
                ('grade', models.FloatField(blank=True, null=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='uniworld.assignment')),
            ],
        ),
    ]