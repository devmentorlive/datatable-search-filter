from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Program',
            fields=[
                ('prog_id', models.CharField(max_length=120, primary_key=True, serialize=False)),
                ('program', models.TextField(max_length=120)),
                ('year_level', models.TextField(null=True, max_length=120)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'cal_program',
            },
        ),
    ]
