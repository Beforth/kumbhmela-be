from django.contrib import admin
from .models import Zone, Amenity


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'color', 'capacity', 'is_active', 'updated_at')
    list_filter = ('status', 'color', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'updated_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description', 'phone')
    ordering = ('category', 'name')
    readonly_fields = ('created_at', 'updated_at')
