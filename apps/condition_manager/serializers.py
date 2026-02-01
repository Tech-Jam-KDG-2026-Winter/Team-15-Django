from rest_framework import serializers
from .models import ConditionLog, Routine, ExerciseMenu


class ConditionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConditionLog
        fields = "__all__"


class RoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Routine
        fields = "__all__"


class ExerciseMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseMenu
        fields = "__all__"
