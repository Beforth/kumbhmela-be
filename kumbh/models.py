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
    
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES)
    capacity = models.IntegerField(help_text="Capacity percentage (0-100)")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="Center point latitude (optional if polygon is provided)")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, help_text="Center point longitude (optional if polygon is provided)")
    polygon = models.JSONField(blank=True, null=True, help_text="Polygon coordinates as array of [lat, lng] pairs")
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
