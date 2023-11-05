# Generated by Django 4.2.6 on 2023-11-05 20:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0006_orderitem_rating"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderitem",
            name="rating",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=3,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(0.0),
                    django.core.validators.MaxValueValidator(5.0),
                ],
            ),
        ),
    ]
