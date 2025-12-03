from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q
from .models import Zone, Amenity
from .serializers import ZoneSerializer, AmenitySerializer, AmenityListSerializer


# Admin Views
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
            return redirect("kumbh:admin_dashboard")

        messages.error(request, "Invalid credentials or not an admin user.")

    return render(request, "admin_login.html")


def _is_staff(user):
    return user.is_staff


@login_required(login_url="kumbh:admin_login")
@user_passes_test(_is_staff, login_url="kumbh:admin_login")
def admin_dashboard_view(request):
    """Basic admin dashboard page shown after successful login."""
    return render(request, "admin_dashboard.html")


@login_required(login_url="kumbh:admin_login")
@user_passes_test(_is_staff, login_url="kumbh:admin_login")
def admin_sos_requests_view(request):
    """Admin page listing SOS requests."""
    return render(request, "admin_sos_requests.html")


@login_required(login_url="kumbh:admin_login")
@user_passes_test(_is_staff, login_url="kumbh:admin_login")
def admin_lost_found_view(request):
    """Admin page listing lost/found reports."""
    return render(request, "admin_lost_found.html")


@login_required(login_url="kumbh:admin_login")
@user_passes_test(_is_staff, login_url="kumbh:admin_login")
def admin_amenities_view(request):
    """
    Admin page showing an overview of on-ground amenities
    (toilets, water points, help desks, etc.).
    """
    return render(request, "admin_amenities.html")


@login_required(login_url="kumbh:admin_login")
@user_passes_test(_is_staff, login_url="kumbh:admin_login")
def admin_crowding_zones_view(request):
    """
    Admin page focused on crowding / congestion across zones.
    """
    return render(request, "admin_crowding_zones.html")


@login_required(login_url="kumbh:admin_login")
def admin_logout_view(request):
    """Logout admin user and redirect to login."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("kumbh:admin_login")


# API Views
class ZoneViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing zones (read-only)"""
    queryset = Zone.objects.filter(is_active=True)
    serializer_class = ZoneSerializer
    permission_classes = [AllowAny]


@api_view(['GET'])
@permission_classes([AllowAny])
def zones_list(request):
    """Get list of all active zones"""
    zones = Zone.objects.filter(is_active=True)
    serializer = ZoneSerializer(zones, many=True)
    return Response({
        'count': zones.count(),
        'results': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def zones_detail(request, pk):
    """Get details of a specific zone"""
    try:
        zone = Zone.objects.get(pk=pk, is_active=True)
        serializer = ZoneSerializer(zone)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Zone.DoesNotExist:
        return Response(
            {'detail': 'Zone not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def amenities_list(request):
    """Get list of amenities with optional category filter"""
    category = request.query_params.get('category', None)
    queryset = Amenity.objects.filter(is_active=True)
    
    if category:
        queryset = queryset.filter(category=category)
    
    serializer = AmenityListSerializer(queryset, many=True)
    return Response({
        'count': queryset.count(),
        'category': category,
        'results': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def amenities_detail(request, pk):
    """Get details of a specific amenity"""
    try:
        amenity = Amenity.objects.get(pk=pk, is_active=True)
        serializer = AmenitySerializer(amenity)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Amenity.DoesNotExist:
        return Response(
            {'detail': 'Amenity not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def amenities_categories(request):
    """Get list of all amenity categories"""
    categories = Amenity.CATEGORY_CHOICES
    return Response({
        'categories': [{'value': value, 'label': label} for value, label in categories]
    }, status=status.HTTP_200_OK)
