# Generated by Django 5.0.6 on 2024-06-26 11:45

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("consultations", "0020_theme_processing_run"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="answer",
            name="old_theme",
        ),
        migrations.DeleteModel(
            name="OldTheme",
        ),
    ]
