from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .models import Operation


def calculator_view(request: HttpRequest) -> HttpResponse:
    result: float | None = None
    error: str | None = None
    a: float | None = None
    b: float | None = None
    operation: str | None = None
    history: list[dict[str, str]] = request.session.get("history", [])

    if request.method == "POST":
        operation = request.POST.get("operation") or None
        a_raw = request.POST.get("a") or ""
        b_raw = request.POST.get("b") or ""

        try:
            a = float(a_raw)
            b = float(b_raw)
        except ValueError:
            error = "Введите корректные числа."
        else:
            if operation == "add":
                result = a + b
            elif operation == "sub":
                result = a - b
            elif operation == "mul":
                result = a * b
            elif operation == "div":
                if b == 0:
                    error = "Деление на ноль невозможно."
                else:
                    result = a / b
            else:
                error = "Выберите операцию."

            if error is None and result is not None:
                entry = {
                    "a": str(a),
                    "b": str(b),
                    "operation": operation or "",
                    "result": str(result),
                }
                history.append(entry)
                history = history[-10:]
                request.session["history"] = history

                # сохраняем в БД для авторизованных пользователей
                if request.user.is_authenticated and operation is not None:
                    Operation.objects.create(
                        user=request.user,
                        a=a,
                        b=b,
                        operation=operation,
                        result=result,
                    )

    context = {
        "a": a,
        "b": b,
        "operation": operation,
        "result": result,
        "error": error,
        "history": history,
    }
    return render(request, "calculator/calculator.html", context)


def signup_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("calculator")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно.")
            return redirect("calculator")
    else:
        form = UserCreationForm()

    return render(request, "calculator/signup.html", {"form": form})


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("calculator")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Вы успешно вошли.")
            return redirect("calculator")
    else:
        form = AuthenticationForm(request)

    return render(request, "calculator/login.html", {"form": form})


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.info(request, "Вы вышли из аккаунта.")
    return redirect("calculator")


@login_required
def history_view(request: HttpRequest) -> HttpResponse:
    qs = Operation.objects.all()
    if not request.user.is_staff:
        qs = qs.filter(user=request.user)

    # простая сортировка и фильтрация через query-параметры
    op = request.GET.get("operation")
    if op:
        qs = qs.filter(operation=op)

    ordering = request.GET.get("ordering") or "-created_at"
    qs = qs.order_by(ordering)

    return render(
        request,
        "calculator/history.html",
        {
            "operations": qs[:100],  # ограничим вывод
        },
    )
