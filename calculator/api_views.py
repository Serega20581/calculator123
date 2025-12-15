from __future__ import annotations

from django.db.models import QuerySet
from rest_framework import permissions, viewsets

from .models import Operation
from .serializers import OperationSerializer


class IsAdminOrOwnerReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Operation) -> bool:
        if request.user and request.user.is_staff:
            return True
        if request.method in permissions.SAFE_METHODS:
            return obj.user == request.user
        return False


class OperationViewSet(viewsets.ModelViewSet):
    serializer_class = OperationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwnerReadOnly]
    search_fields = ["a", "b", "result", "operation", "user__username"]
    ordering_fields = ["created_at", "result", "operation"]
    ordering = ["-created_at"]

    def get_queryset(self) -> QuerySet[Operation]:
        qs = Operation.objects.all()
        user = self.request.user
        if not user.is_staff:
            qs = qs.filter(user=user)
        return qs

    def perform_create(self, serializer: OperationSerializer) -> None:  # type: ignore[override]
        serializer.save(user=self.request.user)
