from django.urls import path
from .views import (
    zones_list,
    zones_detail,
    amenities_list,
    amenities_detail,
    amenities_categories,
    sos_requests_list,
    sos_requests_detail,
    family_members_list,
    family_members_detail,
    update_user_location,
    create_family_invitation,
    accept_family_invitation,
    lost_found_list,
    lost_found_detail,
)

app_name = 'kumbh_api'

urlpatterns = [
    # Zones APIs
    path('zones/', zones_list, name='zones-list'),
    path('zones/<int:pk>/', zones_detail, name='zones-detail'),
    
    # Amenities APIs
    path('amenities/', amenities_list, name='amenities-list'),
    path('amenities/<int:pk>/', amenities_detail, name='amenities-detail'),
    path('amenities/categories/', amenities_categories, name='amenities-categories'),
    
    # SOS Request APIs
    path('sos-requests/', sos_requests_list, name='sos-requests-list'),
    path('sos-requests/<int:pk>/', sos_requests_detail, name='sos-requests-detail'),
    
    # Family Member APIs
    path('family-members/', family_members_list, name='family-members-list'),
    path('family-members/<int:pk>/', family_members_detail, name='family-members-detail'),
    path('family-members/update-location/', update_user_location, name='update-user-location'),
    
    # Family Invitation APIs
    path('family-invitations/create/', create_family_invitation, name='create-family-invitation'),
    path('family-invitations/accept/', accept_family_invitation, name='accept-family-invitation'),
    
    # Lost & Found APIs
    path('lost-found/', lost_found_list, name='lost-found-list'),
    path('lost-found/<int:pk>/', lost_found_detail, name='lost-found-detail'),
]

