from django.db import models
from django_mysql.models import ListTextField
from courses.models import Course
from participants.models import Participant
from groups.models import Group
from programs.models import Program

class Event(models.Model):

    class TrainingSession(models.TextChoices):
        SESSION_1920 = '2019-2020'
        SESSION_2021 = '2020-2021'
        SESSION_2122 = '2021-2022'
        SESSION_2223 = '2022-2023'
        SESSION_2324 = '2023-2024'

    class EventType(models.TextChoices):
        CLINIC = 'CLINIC'
        ASSESSMENT = 'ASSESSMENT'
        CLINIC_ACTIVITY = 'CLINIC ACTIVITY'
        CLINIC_ASSESSMENT = 'CLINIC ASSESSMENT'
        LAB = 'LAB'
        LAB_ASSESSMENT = 'LAB ASSESSMENT'
        LECTURE = 'LECTURE'
        ORIENTATION = 'ORIENTATION'
        REMEDIAL = 'REMEDIAL'
        SEMINAR = 'SEMINAR'
        SIM_CLINIC = 'SIM CLINIC'
        SIM_LAB = 'SIM LAB'

    event_id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id',blank=True, null=True)
    training_session = models.TextField(choices=TrainingSession.choices, null=True)
    event_type = models.TextField(choices=EventType.choices, null=True)
    event_objectives= ListTextField(base_field= models.CharField(max_length = 1000),null=True)
    event_title = models.TextField(null=True)
    event_desc = models.TextField(null=True)
    event_date = models.DateField(null=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    total_duration = models.IntegerField(null=True)
    deleted = models.BooleanField(default=False)
    term = models.TextField(null=True)
    discipline_domain = ListTextField(base_field= models.CharField(max_length = 1000),null=True)
    location = models.TextField(null=True)
    course_director = models.TextField(null=True)
    instructors = ListTextField(base_field= models.CharField(max_length = 1000),blank=True, null=True)
    session_plan = models.TextField(null=True, blank=True)
    number_of_students = models.IntegerField(null=True)
    assistant_operator = models.TextField(blank=True, null=True)
    clinic_sim_lab_equipment = models.TextField(blank=True, null=True)
    prog_id = models.ForeignKey(Program, on_delete=models.PROTECT, db_column='prog_id', null=True)

    class Meta:
        db_table = "cal_event"


class EventGroup(models.Model):
    event_group_id = models.AutoField(primary_key=True)
    location = models.TextField(max_length=120, null=True)
    vodcast_url = models.TextField(max_length=120, null=True)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE, db_column='event_id')
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE, db_column='group_id', null=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "cal_event_group"


class EventGroupInstructor(models.Model):
    event_group_instructor_id = models.AutoField(primary_key=True)
    event_group_id = models.ForeignKey(EventGroup, on_delete=models.CASCADE, db_column='event_group_id')
    instructor_id = models.ForeignKey(Participant, on_delete=models.CASCADE, db_column='instructor_id', null=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "cal_event_group_instructor"


class Tag(models.Model):
    def save(self, *args, **kwargs):
        self.tag_name = self.tag_name.lower()
        return super(Tag, self).save(*args, **kwargs)

    tag_id = models.AutoField(primary_key=True)
    tag_name = models.TextField(max_length=120)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "cal_tag"


class EventTag(models.Model):
    event_tag_id = models.AutoField(primary_key=True)
    tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE, db_column='tag_id')
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE, db_column='event_id')
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "cal_event_tag"
    
class EventFileAttachment(models.Model):
    event_file_attachment_id = models.AutoField(primary_key=True)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE, db_column='event_id')
    event_file_link = models.TextField(blank=True, null=True)
    event_file_name = models.TextField(blank=True, null=True)
    event_file_desc = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = "cal_event_file_attachment"

class EventInstructorFileAttachment(models.Model):
    event_instructor_file_attachment_id = models.AutoField(primary_key=True)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE, db_column='event_id')
    event_instructor_file_link = models.TextField(blank=True, null=True)
    event_instructor_file_name = models.TextField(blank=True, null=True)
    event_instructor_file_desc = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = "cal_event_instructor_file_attachment"

class ZoomMeeting(models.Model):
    meeting_id = models.AutoField(primary_key=True)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE, db_column='event_id')
    meeting_title = models.TextField(max_length=50)
    passcode = models.TextField(max_length=10)
    meeting_url = models.URLField(max_length=100)
    deleted = models.BooleanField(default=False)

class EventVodcast(models.Model):
    event_vodcast_id = models.AutoField(primary_key=True)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE, db_column='event_id')
    vodcast_url = models.TextField()

    class Meta:
        db_table = "cal_event_vodcast"

