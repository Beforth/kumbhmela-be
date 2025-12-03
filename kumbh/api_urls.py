from django.urls import path
from .views import (
    zones_list,
    zones_detail,
    amenities_list,
    amenities_detail,
    amenities_categories,
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
]

