from rest_framework import serializers
from . import models


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Event
        fields = ['event_id', 'course_id', 'training_session', 'event_type', 'event_title','event_objectives', 'event_desc',
                  'event_date', 'start_time', 'end_time', 'total_duration', 'deleted', 'term', 'prog_id',
                  'location', 'course_director', 'instructors', 'discipline_domain', 'session_plan', 'number_of_students', 'assistant_operator', 
                  'clinic_sim_lab_equipment']


class EventGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventGroup
        fields = ['event_group_id', 'event_id', 'group_id', 'location', 'vodcast_url', 'deleted']


class EventGroupInstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventGroupInstructor
        fields = ['event_group_instructor_id', 'event_group_id', 'instructor_id', 'deleted']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ['tag_id', 'tag_name', 'deleted']


class EventTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventTag
        fields = ['event_tag_id', 'tag_id', 'event_id', 'deleted']

class ZoomMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ZoomMeeting
        fields = ['meeting_id', 'event_id', 'meeting_title', 'passcode', 'meeting_url', 'deleted']
        

class EventFileAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventFileAttachment
        fields = ['event_file_attachment_id', 'event_id', 'event_file_link', 'event_file_name', 'event_file_desc']

class EventInstructorFileAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventInstructorFileAttachment
        fields = ['event_instructor_file_attachment_id', 'event_id', 'event_instructor_file_link', 'event_instructor_file_name', 'event_instructor_file_desc']

class EventVodcastSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventVodcast
        fields = ['event_vodcast_id', 'event_id', 'vodcast_url']
