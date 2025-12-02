from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages


def admin_login_view(request):
    """
    Simple admin login page that uses Django's auth system.
    It expects staff/superuser credentials and, on success, redirects to the dashboard.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect("admin_dashboard")

        messages.error(request, "Invalid credentials or not an admin user.")

    return render(request, "admin_login.html")


def _is_staff(user):
    return user.is_staff


@login_required(login_url="admin_login")
@user_passes_test(_is_staff, login_url="admin_login")
def admin_dashboard_view(request):
    """Basic admin dashboard page shown after successful login."""
    return render(request, "admin_dashboard.html")


@login_required(login_url="admin_login")
@user_passes_test(_is_staff, login_url="admin_login")
def admin_sos_requests_view(request):
    """Admin page listing SOS requests."""
    return render(request, "admin_sos_requests.html")


@login_required(login_url="admin_login")
@user_passes_test(_is_staff, login_url="admin_login")
def admin_lost_found_view(request):
    """Admin page listing lost/found reports."""
    return render(request, "admin_lost_found.html")


@login_required(login_url="admin_login")
def admin_logout_view(request):
    """Logout admin user and redirect to login."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("admin_login")

