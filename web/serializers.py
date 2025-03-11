from rest_framework import serializers

from .models import TimezoneShape


class TimezoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimezoneShape
        fields = ('name',)
