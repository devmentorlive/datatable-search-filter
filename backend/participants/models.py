from django.db import models


class Participant(models.Model):
    class Meta:
        db_table = "cal_participant"

    class ParticipantType(models.TextChoices):
        INSTRUCTOR = "Instructor"
        STUDENT = "Student"
        ADMIN = "Admin"


    participant_id = models.AutoField(primary_key=True)
    participant_ccid = models.CharField(max_length=120)
    participant_type = models.TextField(choices=ParticipantType.choices, null=True)
    first = models.TextField(max_length=120, null=True)
    last = models.TextField(max_length=120, null=True)
    deleted = models.BooleanField(default=False)
