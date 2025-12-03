from rest_framework import serializers
from .models import Zone, Amenity


class ZoneSerializer(serializers.ModelSerializer):
    """Serializer for Zone model"""
    lat = serializers.DecimalField(source='latitude', max_digits=9, decimal_places=6, read_only=True, allow_null=True)
    lng = serializers.DecimalField(source='longitude', max_digits=9, decimal_places=6, read_only=True, allow_null=True)
    color_code = serializers.CharField(source='color', read_only=True)
    
    class Meta:
        model = Zone
        fields = ('id', 'name', 'status', 'color', 'color_code', 'capacity', 'lat', 'lng', 'polygon', 'description', 'is_active')
        read_only_fields = ('id', 'created_at', 'updated_at')


class AmenitySerializer(serializers.ModelSerializer):
    """Serializer for Amenity model"""
    lat = serializers.DecimalField(source='latitude', max_digits=9, decimal_places=6, read_only=True)
    lng = serializers.DecimalField(source='longitude', max_digits=9, decimal_places=6, read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Amenity
        fields = ('id', 'name', 'category', 'category_display', 'lat', 'lng', 'description', 'phone', 'is_active')
        read_only_fields = ('id', 'created_at', 'updated_at')


class AmenityListSerializer(serializers.ModelSerializer):
    """Simplified serializer for amenity list (without phone)"""
    lat = serializers.DecimalField(source='latitude', max_digits=9, decimal_places=6, read_only=True)
    lng = serializers.DecimalField(source='longitude', max_digits=9, decimal_places=6, read_only=True)
    
    class Meta:
        model = Amenity
        fields = ('id', 'name', 'category', 'lat', 'lng', 'description', 'is_active')

