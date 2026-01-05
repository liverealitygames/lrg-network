# Generated manually for Phase 2 - Database indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("games", "0008_game_discord_link_game_tiktok_handle"),
    ]

    operations = [
        # Add index to slug field (used in URL lookups)
        migrations.AlterField(
            model_name="game",
            name="slug",
            field=models.SlugField(blank=True, db_index=True),
        ),
        # Add index to game_format field (used in filters)
        migrations.AlterField(
            model_name="game",
            name="game_format",
            field=models.CharField(
                choices=[
                    ("AR", "Amazing Race"),
                    ("BB", "Big Brother"),
                    ("SU", "Survivor"),
                    ("TM", "Task Master"),
                    ("CH", "The Challenge"),
                    ("GE", "The Genius"),
                    ("MO", "The Mole"),
                    ("TR", "The Traitors"),
                    ("OF", "Original Format"),
                    ("VF", "Various Formats"),
                ],
                db_index=True,
                max_length=2,
            ),
        ),
        # Add index to active field (used in filters)
        migrations.AlterField(
            model_name="game",
            name="active",
            field=models.BooleanField(db_index=True, null=True),
        ),
        # Add index to country ForeignKey (used in filters)
        # Note: ForeignKey fields already have indexes, but explicit db_index ensures it
        migrations.AlterField(
            model_name="game",
            name="country",
            field=models.ForeignKey(
                db_index=True,
                on_delete=models.PROTECT,
                to="cities_light.country",
            ),
        ),
        # Add index to region ForeignKey (used in filters)
        migrations.AlterField(
            model_name="game",
            name="region",
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                null=True,
                on_delete=models.PROTECT,
                to="cities_light.region",
            ),
        ),
        # Add index to city ForeignKey (used in filters)
        migrations.AlterField(
            model_name="game",
            name="city",
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                null=True,
                on_delete=models.PROTECT,
                to="cities_light.city",
            ),
        ),
    ]
