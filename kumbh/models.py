from django.db import models
import json


class Zone(models.Model):
    """Crowd zone model for tracking crowd density at different locations"""
    STATUS_CHOICES = [
        ('safe', 'Safe'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    COLOR_CHOICES = [
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('orange', 'Orange'),
        ('red', 'Red'),
    ]
    
    ZONE_TYPE_CHOICES = [
        ('circle', 'Circle'),
        ('polygon', 'Polygon'),
    ]
    
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPE_CHOICES, default='circle', help_text="Type of zone: circle or polygon")
    capacity = models.IntegerField(help_text="Capacity percentage (0-100)")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="Center point latitude (required for circle zones)")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="Center point longitude (required for circle zones)")
    polygon = models.JSONField(blank=True, null=True, help_text="Polygon coordinates as array of [lat, lng] pairs (required for polygon zones)")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_polygon_coordinates(self):
        """Returns polygon as list of LatLng tuples"""
        if self.polygon:
            return self.polygon
        return None
    
    class Meta:
        db_table = 'zones'
        ordering = ['name']
        
    def __str__(self):
        return self.name


class Amenity(models.Model):
    """Amenity model for various services and facilities"""
    CATEGORY_CHOICES = [
        ('medical', 'Medical'),
        ('food', 'Food & Water'),
        ('restroom', 'Restrooms'),
        ('parking', 'Parking'),
        ('accommodation', 'Accommodation'),
        ('transport', 'Transport'),
        ('worship', 'Worship'),
        ('shopping', 'Shopping'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'amenities'
        ordering = ['category', 'name']
        verbose_name_plural = 'Amenities'
        
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class SosRequest(models.Model):
    """SOS emergency request model"""
    TYPE_CHOICES = [
        ('medical', 'Medical Emergency'),
        ('lost', 'Lost Person'),
        ('danger', 'In Danger'),
        ('crowd', 'Crowd Emergency'),
        ('other', 'Other Emergency'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('cancelled', 'Cancelled'),
    ]
    
    user_email = models.EmailField(help_text="Email of the user who sent the SOS")
    user_name = models.CharField(max_length=255, blank=True, null=True, help_text="Name of the user")
    sos_type = models.CharField(max_length=20, choices=TYPE_CHOICES, help_text="Type of emergency")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="Latitude of emergency location")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, help_text="Longitude of emergency location")
    description = models.TextField(blank=True, null=True, help_text="Additional details about the emergency")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', help_text="Current status of the request")
    assigned_team = models.CharField(max_length=255, blank=True, null=True, help_text="Team assigned to handle this request")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sos_requests'
        ordering = ['-created_at']
        verbose_name = 'SOS Request'
        verbose_name_plural = 'SOS Requests'
        
    def __str__(self):
        return f"SOS-{self.id} - {self.get_sos_type_display()} - {self.user_email}"


class FamilyMember(models.Model):
    """Family member model for tracking family members"""
    RELATIONSHIP_CHOICES = [
        ('spouse', 'Spouse'),
        ('parent', 'Parent'),
        ('child', 'Child'),
        ('sibling', 'Sibling'),
        ('grandparent', 'Grandparent'),
        ('grandchild', 'Grandchild'),
        ('uncle', 'Uncle'),
        ('aunt', 'Aunt'),
        ('cousin', 'Cousin'),
        ('friend', 'Friend'),
        ('other', 'Other'),
    ]
    
    user_email = models.EmailField(help_text="Email of the user who added this family member")
    name = models.CharField(max_length=255, help_text="Name of the family member")
    phone = models.CharField(max_length=20, help_text="Phone number of the family member")
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, help_text="Relationship to the user")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="Last known latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="Last known longitude")
    last_location_update = models.DateTimeField(blank=True, null=True, help_text="Last time location was updated")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'family_members'
        ordering = ['-created_at']
        verbose_name = 'Family Member'
        verbose_name_plural = 'Family Members'
        unique_together = [['user_email', 'phone']]  # Prevent duplicate entries
        
    def __str__(self):
        return f"{self.name} ({self.get_relationship_display()}) - {self.user_email}"


class FamilyInvitation(models.Model):
    """Family invitation model for token-based family member addition"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    inviter_email = models.EmailField(help_text="Email of the user who sent the invitation")
    invitee_email = models.EmailField(help_text="Email of the user being invited")
    token = models.CharField(max_length=64, unique=True, help_text="Unique invitation token")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', help_text="Invitation status")
    relationship = models.CharField(max_length=20, blank=True, null=True, help_text="Suggested relationship (optional)")
    expires_at = models.DateTimeField(help_text="When the invitation expires")
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(blank=True, null=True, help_text="When the invitation was accepted")
    
    class Meta:
        db_table = 'family_invitations'
        ordering = ['-created_at']
        verbose_name = 'Family Invitation'
        verbose_name_plural = 'Family Invitations'
        
    def __str__(self):
        return f"Invitation from {self.inviter_email} to {self.invitee_email} - {self.status}"
    
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at


class LostFound(models.Model):
    """Lost and Found report model"""
    TYPE_CHOICES = [
        ('lost', 'Lost'),
        ('found', 'Found'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    report_type = models.CharField(max_length=20, choices=TYPE_CHOICES, help_text="Type of report: lost or found")
    user_email = models.EmailField(help_text="Email of the user who created the report")
    user_name = models.CharField(max_length=255, blank=True, null=True, help_text="Name of the reporter")
    user_phone = models.CharField(max_length=20, blank=True, null=True, help_text="Phone number of the reporter")
    person_name = models.CharField(max_length=255, help_text="Name of the lost/found person or item")
    age = models.IntegerField(blank=True, null=True, help_text="Age of the person (if applicable)")
    description = models.TextField(help_text="Description of the person/item")
    location = models.CharField(max_length=255, help_text="Location where lost/found")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="Latitude of the location")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="Longitude of the location")
    photo_url = models.URLField(blank=True, null=True, help_text="URL of the photo (if uploaded)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', help_text="Current status of the report")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lost_found'
        ordering = ['-created_at']
        verbose_name = 'Lost & Found Report'
        verbose_name_plural = 'Lost & Found Reports'
        
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.person_name} ({self.user_email})"
