from rest_framework import serializers


from .models import ExerciseMenu, Tag, ConditionLog, Routine


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        # Return only the tag name to match API contract
        fields = ("name",)


class ExerciseMenuSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = ExerciseMenu
        fields = "__all__"


class ConditionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConditionLog
        fields = "__all__"


class RoutineSerializer(serializers.ModelSerializer):
    exercise = ExerciseMenuSerializer(read_only=True)

    class Meta:
        model = Routine
        fields = "__all__"


