from rest_framework import serializers

from . import models


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Program
        fields = ['prog_id', 'program', 'year_level', 'deleted']
