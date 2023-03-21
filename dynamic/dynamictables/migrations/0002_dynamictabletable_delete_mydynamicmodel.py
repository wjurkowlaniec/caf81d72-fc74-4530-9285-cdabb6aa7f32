# Generated by Django 4.1.7 on 2023-03-21 15:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dynamictables", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DynamicTableTable",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("uuid", models.CharField(max_length=255)),
                ("is_deleted", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("schema", models.JSONField()),
            ],
        ),
        migrations.DeleteModel(
            name="MyDynamicModel",
        ),
    ]
