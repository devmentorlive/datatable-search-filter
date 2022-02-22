from django.db import models
from events.models import Event
from datetime import datetime


class Assessment(models.Model):
    class Meta:
        db_table = "cal_assessment"
    assessment_id = models.AutoField(primary_key=True)
    event_id = models.CharField(max_length=120)
    assessment_type = models.TextField(max_length=120, null=True)
    status = models.TextField(max_length=120, null=True)
    release_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    created_date = models.DateField(null=True)
    name = models.TextField(max_length=120, null=True)
    group_id = models.CharField(max_length=120)
    deleted = models.BooleanField(default=False)


class AssessmentActivity(models.Model):
    class Meta:
        db_table = "cal_assessment_activity"
    assessment_activity_id = models.AutoField(primary_key=True)
    assessment_id = models.CharField(max_length=120)
    start_date = models.DateField(null=True)
    participant_id = models.CharField(max_length=120)
    participant_id_assessee = models.CharField(max_length=120)
    deleted = models.BooleanField(default=False)
