# Generated by Django 5.1.4 on 2024-12-30 22:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("consultations", "0027_new_models_consultation"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="questiongroup",
            options={"ordering": ["created_at"]},
        ),
    ]
