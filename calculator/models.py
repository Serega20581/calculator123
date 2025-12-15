from __future__ import annotations

from django.conf import settings
from django.db import models


class Operation(models.Model):
    OPERATION_CHOICES = [
        ("add", "+"),
        ("sub", "-"),
        ("mul", "*"),
        ("div", "/"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="operations",
    )
    a = models.DecimalField(max_digits=20, decimal_places=6)
    b = models.DecimalField(max_digits=20, decimal_places=6)
    operation = models.CharField(max_length=3, choices=OPERATION_CHOICES)
    result = models.DecimalField(max_digits=20, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user} {self.a} {self.operation} {self.b} = {self.result}"
