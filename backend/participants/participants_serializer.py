from rest_framework import serializers

from . import models


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Participant
        fields = ['participant_ccid','participant_id', 'participant_type', 'first', 'last', 'deleted']
