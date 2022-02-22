from django.db import models
from participants.models import Participant


class Course(models.Model):
    class Meta:
        db_table = "cal_course"

    class CourseName(models.TextChoices):
        DMED_511 = "Foundations of Medicine and Dentistry"
        DMED_513 = "Endocrine System"
        DMED_515 = "Cardiovascular System"
        DMED_516 = "Pulmonary System"

    class CourseCode(models.TextChoices):
        DMED_511 = "DMED 511"
        DMED_513 = "DMED 513"
        DMED_515 = "DMED 515"
        DMED_516 = "DMED 516"

    class YearLevel(models.IntegerChoices):
        YEAR_ONE = 1
        YEAR_TWO = 2
        YEAR_THREE = 3

    course_id = models.AutoField(primary_key=True)
    course_code = models.TextField(choices=CourseCode.choices, null=True)
    course_name = models.TextField(choices=CourseName.choices)
    course_objectives = models.TextField(max_length=120, null=True)
    course_overview = models.TextField(max_length=120, null=True)
    course_director = models.ForeignKey(Participant, on_delete=models.PROTECT, db_column='course_director', null=True)
    deleted = models.BooleanField(default=False)

    def get_name(self):
        return self.course_name

    def get_code(self):
        return self.course_code


class CourseParticipant(models.Model):
    class Meta:
        db_table = "cal_course_participant"
    course_participant_id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id')
    participant_id = models.ForeignKey(Participant, on_delete=models.CASCADE, db_column='participant_id')
    deleted = models.BooleanField(default=False)
