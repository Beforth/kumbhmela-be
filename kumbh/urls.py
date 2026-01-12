from django.urls import path
from .views import (
    admin_login_view,
    admin_dashboard_view,
    admin_sos_requests_view,
    admin_lost_found_view,
    admin_lost_found_detail_view,
    admin_amenities_view,
    admin_crowding_zones_view,
    admin_events_view,
    admin_logout_view,
    invitation_accept_view,
)

app_name = 'kumbh'

urlpatterns = [
    # Admin views
    path("", admin_login_view, name="admin_login"),
    path("admin-login/", admin_login_view, name="admin_login_page"),
    path("dashboard/", admin_dashboard_view, name="admin_dashboard"),
    path("dashboard/sos-requests/", admin_sos_requests_view, name="admin_sos_requests"),
    path("dashboard/lost-found/", admin_lost_found_view, name="admin_lost_found"),
    path("dashboard/lost-found/<int:report_id>/", admin_lost_found_detail_view, name="admin_lost_found_detail"),
    path("dashboard/amenities/", admin_amenities_view, name="admin_amenities"),
    path("dashboard/crowding-zones/", admin_crowding_zones_view, name="admin_crowding_zones"),
    path("dashboard/events/", admin_events_view, name="admin_events"),
    path("logout/", admin_logout_view, name="admin_logout"),
    path("invite/<str:token>/", invitation_accept_view, name="invitation_accept"),
]
