# Generated by Django 5.1 on 2024-09-01 05:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0016_alter_course_slug_alter_lecture_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecture',
            name='slug',
            field=models.SlugField(blank=True, editable=False, max_length=200, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='lecture',
            name='course',
            field=models.ForeignKey(blank=True, default='rXGhN', null=True, on_delete=django.db.models.deletion.SET_NULL, to='mainapp.course'),
        ),
    ]
