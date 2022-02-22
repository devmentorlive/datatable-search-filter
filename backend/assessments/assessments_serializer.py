from rest_framework import serializers
from . import models
from events import models


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventGroup
        fields = ['assessment_id', 'event_id', 'assessment_type', 'status', 'release_date', 'end_date', 'created_date', 'name', 'group_id']


class AssessmentActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventGroup
        fields = ['assessment_activity_id', 'assessment_id', 'start_date', 'participant_id', 'participant_id_assessee']
