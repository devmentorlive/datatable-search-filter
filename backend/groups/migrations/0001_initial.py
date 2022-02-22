# Generated by Django 3.1.2 on 2020-11-23 23:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('participants', '0001_initial'),
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('group_id', models.AutoField(primary_key=True, serialize=False)),
                ('group_name', models.CharField(max_length=120)),
                ('deleted', models.BooleanField(default=False)),
                ('course_id', models.ForeignKey(db_column='course_id', on_delete=django.db.models.deletion.CASCADE, to='courses.course')),
            ],
            options={
                'db_table': 'cal_group',
            },
        ),
        migrations.CreateModel(
            name='GroupParticipant',
            fields=[
                ('group_participant_id', models.AutoField(primary_key=True, serialize=False)),
                ('deleted', models.BooleanField(default=False)),
                ('group_id', models.ForeignKey(db_column='group_id', on_delete=django.db.models.deletion.CASCADE, to='groups.group')),
                ('participant_id', models.ForeignKey(db_column='participant_id', on_delete=django.db.models.deletion.CASCADE, to='participants.participant')),
            ],
            options={
                'db_table': 'cal_group_participant',
            },
        ),
    ]
