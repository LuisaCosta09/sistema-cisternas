# Generated manually from Guia V3 - parte do Pedro.

import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cisternas", "0002_alter_cisterna_options_alter_cisterna_capacidade_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="alerta",
            options={"ordering": ("-dataHora", "-id")},
        ),
        migrations.AlterModelOptions(
            name="abastecimento",
            options={"ordering": ("-dataHora", "-id")},
        ),
        migrations.AlterField(
            model_name="abastecimento",
            name="quantidadeAgua",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=12,
                validators=[
                    django.core.validators.MinValueValidator(Decimal("0.01")),
                ],
            ),
        ),
    ]
