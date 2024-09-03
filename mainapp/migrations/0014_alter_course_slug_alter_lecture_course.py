# Generated by Django 5.1 on 2024-09-01 05:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0013_alter_course_slug_alter_lecture_course'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='slug',
            field=models.SlugField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='lecture',
            name='course',
            field=models.ForeignKey(blank=True, default='sGMui', null=True, on_delete=django.db.models.deletion.SET_NULL, to='mainapp.course'),
        ),
    ]
