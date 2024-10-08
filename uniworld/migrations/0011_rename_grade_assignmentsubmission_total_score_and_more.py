# Generated by Django 5.0.8 on 2024-09-05 13:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uniworld', '0010_coursematerial_assignment_lecture_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assignmentsubmission',
            old_name='grade',
            new_name='total_score',
        ),
        migrations.RemoveField(
            model_name='assignment',
            name='questions',
        ),
        migrations.RemoveField(
            model_name='assignmentsubmission',
            name='submission',
        ),
        migrations.CreateModel(
            name='AssignmentQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
                ('question_type', models.CharField(choices=[('MCQ', 'Multiple Choice'), ('ESSAY', 'Essay')], max_length=5)),
                ('marks', models.PositiveIntegerField()),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='uniworld.assignment')),
            ],
        ),
        migrations.CreateModel(
            name='MCQOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option_text', models.CharField(max_length=255)),
                ('is_correct', models.BooleanField(default=False)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='uniworld.assignmentquestion')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_text', models.TextField(blank=True, null=True)),
                ('score', models.FloatField(blank=True, null=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='uniworld.assignmentquestion')),
                ('selected_option', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='uniworld.mcqoption')),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='uniworld.assignmentsubmission')),
            ],
        ),
    ]
