from rest_framework import serializers
from . import models


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Group
        fields = ['group_id', 'course_id', 'group_name', 'deleted']


class GroupParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GroupParticipant
        fields = ['group_participant_id', 'group_id', 'participant_id', 'deleted']
