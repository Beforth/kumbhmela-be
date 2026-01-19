from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q
from .models import Zone, Amenity, SosRequest, FamilyMember, FamilyInvitation, LostFound, Event, SmtpSettings, GeographicFeature
from .serializers import ZoneSerializer, AmenitySerializer, AmenityListSerializer, SosRequestSerializer, FamilyMemberSerializer, FamilyInvitationSerializer, LostFoundSerializer, EventSerializer
from django.utils import timezone
from datetime import timedelta
import secrets


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
    """Admin dashboard with real-time statistics and data."""
    from datetime import timedelta
    
    # Calculate time ranges
    now = timezone.now()
    one_hour_ago = now - timedelta(hours=1)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get real statistics
    sos_last_hour = SosRequest.objects.filter(
        created_at__gte=one_hour_ago,
        is_active=True
    ).count()
    
    lost_found_today = LostFound.objects.filter(
        created_at__gte=today_start,
        is_active=True
    ).count()
    
    # Removed zones - using geographic features instead
    overcrowded_zones = 0
    
    # Get recent SOS requests
    recent_sos = SosRequest.objects.filter(
        is_active=True
    ).order_by('-created_at')[:5]
    
    # Get recent lost/found reports
    recent_lost_found = LostFound.objects.filter(
        is_active=True
    ).order_by('-created_at')[:5]
    
    # Get all SOS requests for map markers
    all_sos = SosRequest.objects.filter(is_active=True)
    
    # Get all lost/found for map markers
    all_lost_found = LostFound.objects.filter(is_active=True)
    
    # Get zones (separate from geographic features)
    all_zones = Zone.objects.filter(is_active=True)
    overcrowded_zones_list = Zone.objects.filter(
        status__in=['high', 'critical'],
        is_active=True
    ).order_by('-capacity')[:10]
    overcrowded_zones_count = overcrowded_zones_list.count()
    
    # Get amenities (separate from geographic features)
    all_amenities = Amenity.objects.filter(is_active=True)
    toilets_count = all_amenities.filter(category='restroom').count()
    medical_count = all_amenities.filter(category='medical').count()
    help_desk_count = all_amenities.filter(category='other').count()
    water_points_count = all_amenities.filter(category='food').count()
    
    # Get geographic features from KMZ files (excluding zones and amenities)
    # Note: Zones should be managed via Zone model, not GeographicFeature
    # GeographicFeature objects with feature_type='zone' are separate and should not be shown as zones
    geographic_features = GeographicFeature.objects.filter(
        is_active=True
    ).exclude(feature_type='zone').exclude(
        # Exclude any features that might be amenities
        name__icontains='toilet'
    ).exclude(
        name__icontains='restroom'
    ).exclude(
        name__icontains='medical'
    )
    
    # Group geographic features by type
    roads = geographic_features.filter(feature_type='road')
    parking = geographic_features.filter(feature_type='parking')
    holding_areas = geographic_features.filter(feature_type='holding_area')
    staging_areas = geographic_features.filter(feature_type='staging_area')
    release_points = geographic_features.filter(feature_type='release_point')
    routes = geographic_features.filter(feature_type='route')
    
    # Get upcoming events
    upcoming_events = Event.objects.filter(
        is_active=True,
        event_date__gte=now
    ).order_by('event_date')[:5]
    
    context = {
        'sos_last_hour': sos_last_hour,
        'lost_found_today': lost_found_today,
        'overcrowded_zones_count': overcrowded_zones_count,
        'recent_sos': recent_sos,
        'overcrowded_zones_list': overcrowded_zones_list,
        'recent_lost_found': recent_lost_found,
        'all_sos': all_sos,
        'all_lost_found': all_lost_found,
        'all_zones': all_zones,
        'all_amenities': all_amenities,
        'geographic_features': geographic_features,
        'roads': roads,
        'parking': parking,
        'holding_areas': holding_areas,
        'staging_areas': staging_areas,
        'release_points': release_points,
        'routes': routes,
        'toilets_count': toilets_count,
        'medical_count': medical_count,
        'help_desk_count': help_desk_count,
        'water_points_count': water_points_count,
        'upcoming_events': upcoming_events,
    }
    
    return render(request, "admin_dashboard.html", context)


@login_required(login_url="kumbh:admin_login")
@user_passes_test(_is_staff, login_url="kumbh:admin_login")
def admin_sos_requests_view(request):
    """Admin page listing SOS requests with filtering and search."""
    sos_requests = SosRequest.objects.filter(is_active=True).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        sos_requests = sos_requests.filter(status=status_filter)
    
    # Search by user email or description
    search_query = request.GET.get('search', '')
    if search_query:
        sos_requests = sos_requests.filter(
            Q(user_email__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'sos_requests': sos_requests,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': SosRequest.STATUS_CHOICES,
    }
    
    return render(request, "admin_sos_requests.html", context)


@login_required(login_url="kumbh:admin_login")
@user_passes_test(_is_staff, login_url="kumbh:admin_login")
def admin_lost_found_view(request):
    """Admin page listing lost/found reports with filtering."""
    lost_found = LostFound.objects.filter(is_active=True).order_by('-created_at')
    
    # Filter by type
    type_filter = request.GET.get('type', '')
    if type_filter:
        lost_found = lost_found.filter(report_type=type_filter)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        lost_found = lost_found.filter(status=status_filter)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        lost_found = lost_found.filter(
            Q(person_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    context = {
        'lost_found': lost_found,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'search_query': search_query,
        'type_choices': LostFound.TYPE_CHOICES,
        'status_choices': LostFound.STATUS_CHOICES,
    }
    
    return render(request, "admin_lost_found.html", context)


@login_required(login_url="kumbh:admin_login")
@user_passes_test(_is_staff, login_url="kumbh:admin_login")
def admin_lost_found_detail_view(request, report_id):
    """Admin page showing detailed view of a lost/found report."""
    try:
        report = LostFound.objects.get(id=report_id, is_active=True)
    except LostFound.DoesNotExist:
        messages.error(request, "Report not found.")
        return redirect("kumbh:admin_lost_found")
    
    # Handle status update
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status in [choice[0] for choice in LostFound.STATUS_CHOICES]:
            report.status = new_status
            report.save()
            messages.success(request, f"Report status updated to {report.get_status_display()}.")
            return redirect("kumbh:admin_lost_found_detail", report_id=report_id)
        else:
            messages.error(request, "Invalid status selected.")
    
    context = {
        'report': report,
        'status_choices': LostFound.STATUS_CHOICES,
    }
    
    return render(request, "admin_lost_found_detail.html", context)


@login_required(login_url="kumbh:admin_login")
@user_passes_test(_is_staff, login_url="kumbh:admin_login")
def admin_amenities_view(request):
    """
    Admin page showing an overview of on-ground amenities
    (toilets, water points, help desks, etc.).
    """
    amenities = Amenity.objects.filter(is_active=True).order_by('category', 'name')
    
    # Filter by category
    category_filter = request.GET.get('category', '')
    if category_filter:
        amenities = amenities.filter(category=category_filter)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        amenities = amenities.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Group by category for display
    amenities_by_category = {}
    for amenity in amenities:
        category = amenity.get_category_display()
        if category not in amenities_by_category:
            amenities_by_category[category] = []
        amenities_by_category[category].append(amenity)
    
    context = {
        'amenities': amenities,
        'amenities_by_category': amenities_by_category,
        'category_filter': category_filter,
        'search_query': search_query,
        'category_choices': Amenity.CATEGORY_CHOICES,
    }
    
    return render(request, "admin_amenities.html", context)


@login_required(login_url="kumbh:admin_login")
@user_passes_test(_is_staff, login_url="kumbh:admin_login")
def admin_crowding_zones_view(request):
    """
    Admin page focused on crowding / congestion across zones.
    """
    zones = Zone.objects.filter(is_active=True).order_by('-capacity', 'name')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        zones = zones.filter(status=status_filter)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        zones = zones.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Group by status
    zones_by_status = {
        'critical': zones.filter(status='critical'),
        'high': zones.filter(status='high'),
        'moderate': zones.filter(status='moderate'),
        'safe': zones.filter(status='safe'),
    }
    
    context = {
        'zones': zones,
        'zones_by_status': zones_by_status,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': Zone.STATUS_CHOICES,
    }
    
    return render(request, "admin_crowding_zones.html", context)


@login_required(login_url="kumbh:admin_login")
@user_passes_test(_is_staff, login_url="kumbh:admin_login")
def admin_events_view(request):
    """
    Admin page for managing Kumbh Mela events.
    """
    events = Event.objects.filter(is_active=True).order_by('event_date')
    
    # Handle POST request to create/update event
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        event_date_str = request.POST.get('event_date')
        location = request.POST.get('location', '')
        
        if title and description and event_date_str:
            try:
                from django.utils.dateparse import parse_datetime
                event_date = parse_datetime(event_date_str)
                if event_date is None:
                    # Try parsing as date with time
                    from datetime import datetime
                    event_date = datetime.strptime(event_date_str, '%Y-%m-%dT%H:%M')
                
                if event_id:
                    # Update existing event
                    event = Event.objects.get(id=event_id, is_active=True)
                    event.title = title
                    event.description = description
                    event.event_date = event_date
                    event.location = location
                    event.save()
                    messages.success(request, "Event updated successfully.")
                else:
                    # Create new event
                    Event.objects.create(
                        title=title,
                        description=description,
                        event_date=event_date,
                        location=location,
                    )
                    messages.success(request, "Event created successfully.")
                return redirect("kumbh:admin_events")
            except Exception as e:
                messages.error(request, f"Error saving event: {str(e)}")
        else:
            messages.error(request, "Please fill in all required fields.")
    
    # Handle delete
    delete_id = request.GET.get('delete')
    if delete_id:
        try:
            event = Event.objects.get(id=delete_id, is_active=True)
            event.is_active = False
            event.save()
            messages.success(request, "Event deleted successfully.")
            return redirect("kumbh:admin_events")
        except Event.DoesNotExist:
            messages.error(request, "Event not found.")
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    context = {
        'events': events,
        'search_query': search_query,
    }
    
    return render(request, "admin_events.html", context)


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


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def zones_list(request):
    """Get list of all active zones or create a new zone"""
    if request.method == 'GET':
        zones = Zone.objects.filter(is_active=True)
        serializer = ZoneSerializer(zones, many=True)
        return Response({
            'count': zones.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = ZoneSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def zones_detail(request, pk):
    """Get, update, or delete a specific zone"""
    try:
        zone = Zone.objects.get(pk=pk, is_active=True)
    except Zone.DoesNotExist:
        return Response(
            {'detail': 'Zone not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = ZoneSerializer(zone)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = ZoneSerializer(zone, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PATCH':
        serializer = ZoneSerializer(zone, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        zone.is_active = False  # Soft delete
        zone.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def amenities_list(request):
    """Get list of amenities with optional category filter or create a new amenity"""
    if request.method == 'GET':
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
    
    elif request.method == 'POST':
        serializer = AmenitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
@permission_classes([AllowAny])
def amenities_detail(request, pk):
    """Get details of a specific amenity or delete it"""
    try:
        amenity = Amenity.objects.get(pk=pk, is_active=True)
    except Amenity.DoesNotExist:
        return Response(
            {'detail': 'Amenity not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = AmenitySerializer(amenity)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'DELETE':
        amenity.is_active = False  # Soft delete
        amenity.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def amenities_categories(request):
    """Get list of all amenity categories"""
    categories = Amenity.CATEGORY_CHOICES
    return Response({
        'categories': [{'value': value, 'label': label} for value, label in categories]
    }, status=status.HTTP_200_OK)


# SOS Request APIs
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def sos_requests_list(request):
    """Get list of SOS requests or create a new SOS request"""
    if request.method == 'GET':
        status_filter = request.query_params.get('status', None)
        queryset = SosRequest.objects.filter(is_active=True)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        serializer = SosRequestSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = SosRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print('SOS Request validation errors:', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
@permission_classes([AllowAny])
def sos_requests_detail(request, pk):
    """Get details of a specific SOS request or update its status"""
    try:
        sos_request = SosRequest.objects.get(pk=pk, is_active=True)
    except SosRequest.DoesNotExist:
        return Response(
            {'detail': 'SOS request not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = SosRequestSerializer(sos_request)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':
        serializer = SosRequestSerializer(sos_request, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Family Member APIs
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def family_members_list(request):
    """Get list of family members for a user or create a new family member"""
    if request.method == 'GET':
        user_email = request.query_params.get('user_email', None)
        if not user_email:
            return Response(
                {'detail': 'user_email parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = FamilyMember.objects.filter(user_email=user_email, is_active=True)
        serializer = FamilyMemberSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = FamilyMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def family_members_detail(request, pk):
    """Get, update, or delete a specific family member"""
    try:
        family_member = FamilyMember.objects.get(pk=pk, is_active=True)
    except FamilyMember.DoesNotExist:
        return Response(
            {'detail': 'Family member not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = FamilyMemberSerializer(family_member)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':
        serializer = FamilyMemberSerializer(family_member, data=request.data, partial=True)
        if serializer.is_valid():
            # If location is being updated, set last_location_update
            if 'latitude' in request.data or 'longitude' in request.data:
                family_member.last_location_update = timezone.now()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        family_member.is_active = False
        family_member.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny])
def update_user_location(request):
    """Update location for current user in all their family member records"""
    user_email = request.data.get('user_email')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    if not user_email:
        return Response(
            {'detail': 'user_email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if latitude is None or longitude is None:
        return Response(
            {'detail': 'latitude and longitude are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get current user's details to find records where they appear as a family member
        from user.models import User
        try:
            current_user = User.objects.get(email=user_email)
            user_name = getattr(current_user, 'full_name', None) or user_email.split('@')[0]
        except User.DoesNotExist:
            user_name = user_email.split('@')[0]
        
        # Phone is generated as: email_prefix_hash
        # So we need to find records where phone matches this pattern
        # The phone format is: email_prefix + '_' + hash
        email_prefix = user_email.split('@')[0]
        
        # Update records where current user appears as a family member in others' lists
        # These are records where user_email != current_user_email
        # and phone starts with the email prefix (since phone is generated from email)
        updated_count = FamilyMember.objects.filter(
            is_active=True,
            phone__startswith=email_prefix + '_'
        ).exclude(user_email=user_email).update(
            latitude=latitude,
            longitude=longitude,
            last_location_update=timezone.now()
        )
        
        return Response({
            'detail': f'Location updated for {updated_count} family member record(s)',
            'updated_count': updated_count
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'detail': f'Error updating location: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Family Invitation APIs
@api_view(['POST'])
@permission_classes([AllowAny])
def create_family_invitation(request):
    """Create a new family invitation and generate a token-based link"""
    inviter_email = request.data.get('inviter_email')
    invitee_email = request.data.get('invitee_email')
    relationship = request.data.get('relationship', None)
    
    if not inviter_email or not invitee_email:
        return Response(
            {'detail': 'inviter_email and invitee_email are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if invitee is already a family member
    existing_member = FamilyMember.objects.filter(
        user_email=inviter_email,
        phone__in=FamilyMember.objects.filter(user_email=invitee_email).values_list('phone', flat=True),
        is_active=True
    ).first()
    
    if existing_member:
        return Response(
            {'detail': 'This user is already in your family'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate unique token
    token = secrets.token_urlsafe(32)
    
    # Create invitation (expires in 7 days)
    invitation = FamilyInvitation.objects.create(
        inviter_email=inviter_email,
        invitee_email=invitee_email,
        token=token,
        relationship=relationship,
        expires_at=timezone.now() + timedelta(days=7),
    )
    
    serializer = FamilyInvitationSerializer(invitation)
    
    # Generate single HTTPS invitation link that will redirect to app
    base_url = request.build_absolute_uri('/').rstrip('/')
    invitation_link = f"{base_url}/invite/{token}/"
    
    return Response({
        'invitation': serializer.data,
        'invitation_link': invitation_link,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def accept_family_invitation(request):
    """Get invitation details by token or accept invitation with login"""
    token = request.query_params.get('token') or request.data.get('token')
    
    if not token:
        return Response(
            {'detail': 'token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        invitation = FamilyInvitation.objects.get(token=token, status='pending')
    except FamilyInvitation.DoesNotExist:
        return Response(
            {'detail': 'Invalid or expired invitation token'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if invitation is expired
    if invitation.is_expired():
        invitation.status = 'expired'
        invitation.save()
        return Response(
            {'detail': 'This invitation has expired'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if request.method == 'GET':
        # Return invitation details (for display before login)
        serializer = FamilyInvitationSerializer(invitation)
        return Response({
            'invitation': serializer.data,
            'inviter_email': invitation.inviter_email,
            'invitee_email': invitation.invitee_email,
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Accept invitation - requires email and password
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'detail': 'email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify email matches invitation
        if email.lower() != invitation.invitee_email.lower():
            return Response(
                {'detail': 'Email does not match the invitation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {'detail': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get user's full name first
        user_full_name = getattr(user, 'full_name', None) or email.split('@')[0]
        
        # Generate unique phone identifier based on email
        # This ensures each user gets a unique phone value for the unique_together constraint
        user_phone = email.split('@')[0] + '_' + str(abs(hash(email)) % 10000)
        
        # Check if already a family member - check by name in inviter's family list
        existing = FamilyMember.objects.filter(
            user_email=invitation.inviter_email,
            name=user_full_name,
            is_active=True
        ).first()
        
        if existing:
            invitation.status = 'accepted'
            invitation.accepted_at = timezone.now()
            invitation.save()
            return Response(
                {'detail': 'You are already in this family'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create family member relationship (bidirectional)
        # Add invitee to inviter's family
        try:
            family_member1 = FamilyMember.objects.create(
                user_email=invitation.inviter_email,
                name=user_full_name,
                phone=user_phone,
                relationship=invitation.relationship or 'friend',
            )
        except Exception as e:
            # If unique constraint fails, try to get existing or use different phone
            existing_member = FamilyMember.objects.filter(
                user_email=invitation.inviter_email,
                phone=user_phone,
                is_active=True
            ).first()
            if existing_member:
                family_member1 = existing_member
            else:
                # If still fails, use a different phone value
                user_phone = email.replace('@', '_at_').replace('.', '_')[:20]
                family_member1 = FamilyMember.objects.create(
                    user_email=invitation.inviter_email,
                    name=user_full_name,
                    phone=user_phone,
                    relationship=invitation.relationship or 'friend',
                )
        
        # Add inviter to invitee's family (reverse relationship)
        inviter_user = None
        try:
            from user.models import User
            inviter_user = User.objects.filter(email=invitation.inviter_email).first()
        except:
            pass
        
        inviter_name = getattr(inviter_user, 'full_name', None) if inviter_user else invitation.inviter_email.split('@')[0]
        # Generate unique phone for inviter too
        inviter_phone = invitation.inviter_email.split('@')[0] + '_' + str(abs(hash(invitation.inviter_email)) % 10000)
        
        try:
            family_member2 = FamilyMember.objects.create(
                user_email=invitation.invitee_email,
                name=inviter_name,
                phone=inviter_phone,
                relationship='friend',  # Default reverse relationship
            )
        except Exception as e:
            # If unique constraint fails, try to get existing
            existing_member2 = FamilyMember.objects.filter(
                user_email=invitation.invitee_email,
                phone=inviter_phone,
                is_active=True
            ).first()
            if existing_member2:
                family_member2 = existing_member2
            else:
                # If still fails, use a different phone value
                inviter_phone = invitation.inviter_email.replace('@', '_at_').replace('.', '_')[:20]
                family_member2 = FamilyMember.objects.create(
                    user_email=invitation.invitee_email,
                    name=inviter_name,
                    phone=inviter_phone,
                    relationship='friend',
                )
        
        # Mark invitation as accepted
        invitation.status = 'accepted'
        invitation.accepted_at = timezone.now()
        invitation.save()
        
        return Response({
            'detail': 'Successfully joined the family',
            'family_member': FamilyMemberSerializer(family_member1).data,
        }, status=status.HTTP_200_OK)


# Lost & Found APIs
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def lost_found_list(request):
    """Get list of lost/found reports or create a new report"""
    if request.method == 'GET':
        report_type = request.query_params.get('type', None)  # 'lost' or 'found'
        status_filter = request.query_params.get('status', 'open')  # Filter by status
        search = request.query_params.get('search', None)  # Search query
        
        queryset = LostFound.objects.filter(is_active=True)
        
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if search:
            queryset = queryset.filter(
                Q(person_name__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        
        serializer = LostFoundSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = LostFoundSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def lost_found_detail(request, pk):
    """Get, update, or delete a specific lost/found report"""
    try:
        report = LostFound.objects.get(pk=pk, is_active=True)
    except LostFound.DoesNotExist:
        return Response(
            {'detail': 'Report not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = LostFoundSerializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PATCH':
        serializer = LostFoundSerializer(report, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        report.is_active = False
        report.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def events_list(request):
    """Get list of all active events"""
    events = Event.objects.filter(is_active=True).order_by('event_date')
    
    # Filter by upcoming/past
    filter_type = request.GET.get('type', '')
    now = timezone.now()
    
    if filter_type == 'upcoming':
        events = events.filter(event_date__gte=now)
    elif filter_type == 'past':
        events = events.filter(event_date__lt=now)
    
    serializer = EventSerializer(events, many=True)
    return Response({
        'count': events.count(),
        'results': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def events_detail(request, pk):
    """Get a specific event"""
    try:
        event = Event.objects.get(pk=pk, is_active=True)
    except Event.DoesNotExist:
        return Response(
            {'detail': 'Event not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = EventSerializer(event)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Web view for invitation acceptance
def invitation_accept_view(request, token):
    """Web view that handles invitation links - redirects to app or shows web form"""
    try:
        invitation = FamilyInvitation.objects.get(token=token, status='pending')
    except FamilyInvitation.DoesNotExist:
        return render(request, 'invitation_error.html', {
            'error': 'Invalid or expired invitation link'
        })
    
    # Check if invitation is expired
    if invitation.is_expired():
        invitation.status = 'expired'
        invitation.save()
        return render(request, 'invitation_error.html', {
            'error': 'This invitation has expired'
        })
    
    # Check if request is from mobile device
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(mobile in user_agent for mobile in ['android', 'iphone', 'ipad', 'mobile'])
    
    # Check if user wants web version
    web_mode = request.GET.get('web') == 'true'
    
    # If mobile and not web mode, try to redirect to app
    if is_mobile and not web_mode and request.method == 'GET':
        # Try to redirect to app first
        app_deep_link = f"kumbhsuraksha://invite?token={token}"
        return render(request, 'invitation_redirect.html', {
            'invitation': invitation,
            'app_deep_link': app_deep_link,
            'token': token,
        })
    
    # Show web form for accepting invitation
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            return render(request, 'invitation_accept.html', {
                'invitation': invitation,
                'error': 'Please enter email and password',
                'token': token,
            })
        
        # Verify email matches invitation
        if email.lower() != invitation.invitee_email.lower():
            return render(request, 'invitation_accept.html', {
                'invitation': invitation,
                'error': 'Email does not match the invitation',
                'token': token,
            })
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        if user is None:
            return render(request, 'invitation_accept.html', {
                'invitation': invitation,
                'error': 'Invalid email or password',
                'token': token,
            })
        
        # Get user's full name first
        user_full_name = getattr(user, 'full_name', None) or email.split('@')[0]
        
        # Generate unique phone identifier based on email
        # This ensures each user gets a unique phone value for the unique_together constraint
        user_phone = email.split('@')[0] + '_' + str(abs(hash(email)) % 10000)
        
        # Check if already a family member - check by name in inviter's family list
        existing = FamilyMember.objects.filter(
            user_email=invitation.inviter_email,
            name=user_full_name,
            is_active=True
        ).first()
        
        if existing:
            invitation.status = 'accepted'
            invitation.accepted_at = timezone.now()
            invitation.save()
            return render(request, 'invitation_success.html', {
                'message': 'You are already in this family',
            })
        
        # Create family member relationship (bidirectional)
        # Add invitee to inviter's family list
        try:
            family_member1 = FamilyMember.objects.create(
                user_email=invitation.inviter_email,
                name=user_full_name,
                phone=user_phone,
                relationship=invitation.relationship or 'friend',
            )
        except Exception as e:
            # If unique constraint fails, try to get existing
            existing_member = FamilyMember.objects.filter(
                user_email=invitation.inviter_email,
                phone=user_phone,
                is_active=True
            ).first()
            if existing_member:
                family_member1 = existing_member
            else:
                # If still fails, use a different phone value
                user_phone = email.replace('@', '_at_').replace('.', '_')[:20]
                family_member1 = FamilyMember.objects.create(
                    user_email=invitation.inviter_email,
                    name=user_full_name,
                    phone=user_phone,
                    relationship=invitation.relationship or 'friend',
                )
        
        # Add inviter to invitee's family (reverse relationship)
        inviter_user = None
        try:
            from user.models import User
            inviter_user = User.objects.filter(email=invitation.inviter_email).first()
        except:
            pass
        
        inviter_name = getattr(inviter_user, 'full_name', None) if inviter_user else invitation.inviter_email.split('@')[0]
        # Use similar unique phone generation for inviter
        inviter_phone = invitation.inviter_email.split('@')[0] + '_' + str(abs(hash(invitation.inviter_email)) % 10000)
        
        try:
            family_member2 = FamilyMember.objects.create(
                user_email=invitation.invitee_email,
                name=inviter_name,
                phone=inviter_phone,
                relationship='friend',
            )
        except Exception as e:
            # If unique constraint fails, try to get existing
            existing_member2 = FamilyMember.objects.filter(
                user_email=invitation.invitee_email,
                phone=inviter_phone,
                is_active=True
            ).first()
            if existing_member2:
                family_member2 = existing_member2
            else:
                # If still fails, use a different phone value
                inviter_phone = invitation.inviter_email.replace('@', '_at_').replace('.', '_')[:20]
                family_member2 = FamilyMember.objects.create(
                    user_email=invitation.invitee_email,
                    name=inviter_name,
                    phone=inviter_phone,
                    relationship='friend',
                )
        
        # Mark invitation as accepted
        invitation.status = 'accepted'
        invitation.accepted_at = timezone.now()
        invitation.save()
        
        return render(request, 'invitation_success.html', {
            'message': 'Successfully joined the family!',
        })
    
    # Show invitation acceptance form
    return render(request, 'invitation_accept.html', {
        'invitation': invitation,
        'token': token,
    })

