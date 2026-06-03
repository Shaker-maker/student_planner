# Generated migration: Add Unit Catalog for code-name associations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0002_timetableentry_duration_minutes_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnitCatalog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_code', models.CharField(max_length=20, unique=True, help_text='e.g., CCS 2422, CSE 2418')),
                ('unit_name', models.CharField(max_length=255, help_text='Full unit name e.g., Data Structures')),
                ('department', models.CharField(blank=True, max_length=100, help_text='Department offering the unit')),
                ('credits', models.IntegerField(blank=True, null=True, help_text='Unit credits/points')),
                ('description', models.TextField(blank=True, help_text='Unit description')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this unit is currently offered')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Unit Catalog Entry',
                'verbose_name_plural': 'Unit Catalog',
                'ordering': ['unit_code'],
            },
        ),
    ]
