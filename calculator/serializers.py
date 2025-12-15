from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Operation


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class OperationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Operation
        fields = [
            "id",
            "user",
            "a",
            "b",
            "operation",
            "result",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]
