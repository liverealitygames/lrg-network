# Generated manually for Phase 3 - Meta options

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0009_add_game_indexes"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="game",
            options={
                "ordering": ["name"],
                "verbose_name": "Game",
                "verbose_name_plural": "Games",
            },
        ),
        migrations.AlterModelOptions(
            name="gamedate",
            options={
                "ordering": ["-start_date", "-end_date"],
                "verbose_name": "Game Date",
                "verbose_name_plural": "Game Dates",
            },
        ),
        migrations.AlterModelOptions(
            name="gameimages",
            options={
                "ordering": ["game", "created"],
                "verbose_name": "Game Image",
                "verbose_name_plural": "Game Images",
            },
        ),
        migrations.AlterModelOptions(
            name="season",
            options={
                "ordering": ["game", "number"],
                "verbose_name": "Season",
                "verbose_name_plural": "Seasons",
            },
        ),
    ]
