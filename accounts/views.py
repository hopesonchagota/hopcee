from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from orders.models import Order

from .forms import ProfileUpdateForm, StudentLoginForm, StudentRegistrationForm


def register(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome to Hopcee, {user.first_name}! Your account is ready — start ordering below.",
            )
            return redirect("core:home")
    else:
        form = StudentRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


class StudentLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = StudentLoginForm
    redirect_authenticated_user = True


class StudentLogoutView(LogoutView):
    next_page = reverse_lazy("core:home")


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    orders = Order.objects.filter(customer=request.user).order_by("-created_at")[:10]
    return render(request, "accounts/profile.html", {"form": form, "orders": orders})
