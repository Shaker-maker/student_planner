# Generated migration: Link TimetableEntry to UnitCatalog

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0003_unitcatalog'),
    ]

    operations = [
        migrations.AddField(
            model_name='timetableentry',
            name='unit_catalog',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timetable_entries', to='timetable.unitcatalog'),
        ),
    ]
