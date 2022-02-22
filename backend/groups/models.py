from django.db import models
from courses.models import Course
from participants.models import Participant


class Group(models.Model):
    class Meta:
        db_table = "cal_group"
    group_id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id')
    group_name = models.CharField(max_length=120)
    deleted = models.BooleanField(default=False)


class GroupParticipant(models.Model):
    class Meta:
        db_table = "cal_group_participant"
    group_participant_id = models.AutoField(primary_key=True)
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE, db_column='group_id')
    participant_id = models.ForeignKey(Participant, on_delete=models.CASCADE, db_column='participant_id')
    deleted = models.BooleanField(default=False)
