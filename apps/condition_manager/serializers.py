from rest_framework import serializers

from .models import ExerciseMenu, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")


class ExerciseMenuSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = ExerciseMenu
        fields = (
            "id",
            "name",
            "description",
            "beginner_guide",
            "category",
            "target_area",
            "tags",
        )
