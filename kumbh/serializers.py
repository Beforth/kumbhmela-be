from rest_framework import serializers
from .models import Zone, Amenity, SosRequest, FamilyMember, FamilyInvitation, LostFound


class ZoneSerializer(serializers.ModelSerializer):
    """Serializer for Zone model"""
    lat = serializers.DecimalField(source='latitude', max_digits=9, decimal_places=6, allow_null=True, required=False, read_only=True)
    lng = serializers.DecimalField(source='longitude', max_digits=9, decimal_places=6, allow_null=True, required=False, read_only=True)
    color_code = serializers.CharField(source='color', read_only=True)
    # Allow direct writing to latitude/longitude fields
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, allow_null=True, required=False)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, allow_null=True, required=False)
    
    class Meta:
        model = Zone
        fields = ('id', 'name', 'status', 'color', 'color_code', 'zone_type', 'capacity', 'lat', 'lng', 'latitude', 'longitude', 'polygon', 'description', 'is_active')
        read_only_fields = ('id', 'created_at', 'updated_at', 'color_code', 'lat', 'lng')
    
    def validate(self, data):
        """Validate that circle zones have coordinates and polygon zones have polygon data"""
        zone_type = data.get('zone_type', 'circle')
        
        if zone_type == 'circle':
            if not data.get('latitude') or not data.get('longitude'):
                raise serializers.ValidationError({
                    'latitude': 'Latitude is required for circle zones.',
                    'longitude': 'Longitude is required for circle zones.'
                })
        elif zone_type == 'polygon':
            if not data.get('polygon') or not isinstance(data.get('polygon'), list) or len(data.get('polygon', [])) < 3:
                raise serializers.ValidationError({
                    'polygon': 'Polygon coordinates are required for polygon zones (minimum 3 points).'
                })
        
        return data


class AmenitySerializer(serializers.ModelSerializer):
    """Serializer for Amenity model"""
    lat = serializers.DecimalField(source='latitude', max_digits=9, decimal_places=6, read_only=True)
    lng = serializers.DecimalField(source='longitude', max_digits=9, decimal_places=6, read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True)
    
    class Meta:
        model = Amenity
        fields = ('id', 'name', 'category', 'category_display', 'lat', 'lng', 'latitude', 'longitude', 'description', 'phone', 'is_active')
        read_only_fields = ('id', 'created_at', 'updated_at', 'lat', 'lng', 'category_display')


class AmenityListSerializer(serializers.ModelSerializer):
    """Simplified serializer for amenity list (without phone)"""
    lat = serializers.DecimalField(source='latitude', max_digits=9, decimal_places=6, read_only=True)
    lng = serializers.DecimalField(source='longitude', max_digits=9, decimal_places=6, read_only=True)
    
    class Meta:
        model = Amenity
        fields = ('id', 'name', 'category', 'lat', 'lng', 'description', 'is_active')


class SosRequestSerializer(serializers.ModelSerializer):
    """Serializer for SOS Request model"""
    lat = serializers.DecimalField(source='latitude', max_digits=9, decimal_places=6, read_only=True)
    lng = serializers.DecimalField(source='longitude', max_digits=9, decimal_places=6, read_only=True)
    sos_type_display = serializers.CharField(source='get_sos_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True, allow_null=False)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=True, allow_null=False)
    user_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = SosRequest
        fields = ('id', 'user_email', 'user_name', 'sos_type', 'sos_type_display', 'lat', 'lng', 'latitude', 'longitude', 
                  'description', 'status', 'status_display', 'assigned_team', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'lat', 'lng', 'sos_type_display', 'status_display')


class FamilyMemberSerializer(serializers.ModelSerializer):
    """Serializer for Family Member model"""
    lat = serializers.DecimalField(source='latitude', max_digits=9, decimal_places=6, read_only=True, allow_null=True)
    lng = serializers.DecimalField(source='longitude', max_digits=9, decimal_places=6, read_only=True, allow_null=True)
    relationship_display = serializers.CharField(source='get_relationship_display', read_only=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    
    class Meta:
        model = FamilyMember
        fields = ('id', 'user_email', 'name', 'phone', 'relationship', 'relationship_display', 
                  'lat', 'lng', 'latitude', 'longitude', 'last_location_update', 
                  'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'lat', 'lng', 'relationship_display', 'last_location_update')


class FamilyInvitationSerializer(serializers.ModelSerializer):
    """Serializer for Family Invitation model"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = FamilyInvitation
        fields = ('id', 'inviter_email', 'invitee_email', 'token', 'status', 'status_display', 
                  'relationship', 'expires_at', 'is_expired', 'created_at', 'accepted_at')
        read_only_fields = ('id', 'token', 'status', 'status_display', 'is_expired', 'created_at', 'accepted_at')


class LostFoundSerializer(serializers.ModelSerializer):
    """Serializer for LostFound model"""
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = LostFound
        fields = ('id', 'report_type', 'report_type_display', 'user_email', 'user_name', 'user_phone',
                  'person_name', 'age', 'description', 'location', 'latitude', 'longitude',
                  'photo_url', 'status', 'status_display', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'report_type_display', 'status_display', 'created_at', 'updated_at')

