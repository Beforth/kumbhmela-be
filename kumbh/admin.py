from django.contrib import admin
from .models import Zone, Amenity, SosRequest, FamilyMember, FamilyInvitation, LostFound


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone_type', 'status', 'color', 'capacity', 'is_active', 'updated_at')
    list_filter = ('zone_type', 'status', 'color', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'zone_type', 'status', 'color', 'capacity', 'description', 'is_active')
        }),
        ('Circle Zone', {
            'fields': ('latitude', 'longitude'),
            'description': 'Required for circle zones'
        }),
        ('Polygon Zone', {
            'fields': ('polygon',),
            'description': 'Required for polygon zones. Format: [[lat1, lng1], [lat2, lng2], ...]'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'updated_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description', 'phone')
    ordering = ('category', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SosRequest)
class SosRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'sos_type', 'user_email', 'status', 'created_at', 'updated_at')
    list_filter = ('sos_type', 'status', 'is_active', 'created_at')
    search_fields = ('user_email', 'user_name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Request Information', {
            'fields': ('user_email', 'user_name', 'sos_type', 'description', 'status', 'assigned_team', 'is_active')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user_email', 'phone', 'relationship', 'is_active', 'last_location_update', 'created_at')
    list_filter = ('relationship', 'is_active', 'user_email')
    search_fields = ('name', 'user_email', 'phone')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_location_update')
    fieldsets = (
        ('Member Details', {
            'fields': ('user_email', 'name', 'phone', 'relationship')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'last_location_update')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LostFound)
class LostFoundAdmin(admin.ModelAdmin):
    list_display = ('id', 'report_type', 'person_name', 'user_email', 'location', 'status', 'created_at')
    list_filter = ('report_type', 'status', 'is_active', 'created_at')
    search_fields = ('person_name', 'user_email', 'description', 'location')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Report Details', {
            'fields': ('report_type', 'status', 'is_active')
        }),
        ('Person/Item Information', {
            'fields': ('person_name', 'age', 'description', 'photo_url')
        }),
        ('Location', {
            'fields': ('location', 'latitude', 'longitude')
        }),
        ('Reporter Information', {
            'fields': ('user_email', 'user_name', 'user_phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FamilyInvitation)
class FamilyInvitationAdmin(admin.ModelAdmin):
    list_display = ('id', 'inviter_email', 'invitee_email', 'status', 'expires_at', 'created_at', 'accepted_at')
    list_filter = ('status', 'created_at')
    search_fields = ('inviter_email', 'invitee_email', 'token')
    ordering = ('-created_at',)
    readonly_fields = ('token', 'created_at', 'accepted_at')
    fieldsets = (
        ('Invitation Details', {
            'fields': ('inviter_email', 'invitee_email', 'token', 'relationship', 'status')
        }),
        ('Timing', {
            'fields': ('expires_at', 'created_at', 'accepted_at')
        }),
    )
