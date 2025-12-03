from django.core.management.base import BaseCommand
from kumbh.models import Zone, Amenity


class Command(BaseCommand):
    help = 'Load initial zones and amenities data'

    def handle(self, *args, **options):
        # Create Zones
        zones_data = [
            {'name': 'Har Ki Pauri', 'status': 'moderate', 'color': 'orange', 'capacity': 45, 'latitude': 29.9576, 'longitude': 78.1712},
            {'name': 'Triveni Ghat', 'status': 'safe', 'color': 'green', 'capacity': 25, 'latitude': 29.9350, 'longitude': 78.1550},
            {'name': 'Ram Jhula', 'status': 'high', 'color': 'red', 'capacity': 75, 'latitude': 29.9650, 'longitude': 78.1850},
            {'name': 'Main Bazaar', 'status': 'critical', 'color': 'red', 'capacity': 95, 'latitude': 29.9500, 'longitude': 78.1600},
            {'name': 'Lakshman Jhula', 'status': 'moderate', 'color': 'yellow', 'capacity': 50, 'latitude': 29.9800, 'longitude': 78.1900},
            {'name': 'Bharat Mandir', 'status': 'safe', 'color': 'green', 'capacity': 30, 'latitude': 29.9400, 'longitude': 78.1400},
        ]
        
        for zone_data in zones_data:
            zone, created = Zone.objects.get_or_create(
                name=zone_data['name'],
                defaults=zone_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created zone: {zone.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Zone already exists: {zone.name}'))

        # Create Amenities
        amenities_data = [
            # Medical
            {'name': 'City Hospital', 'category': 'medical', 'latitude': 29.9500, 'longitude': 78.1600, 'description': '24/7 Emergency services', 'phone': '+91-1234567890'},
            {'name': 'First Aid Post 1', 'category': 'medical', 'latitude': 29.9576, 'longitude': 78.1712, 'description': 'Near Har Ki Pauri'},
            {'name': 'First Aid Post 2', 'category': 'medical', 'latitude': 29.9350, 'longitude': 78.1550, 'description': 'Near Triveni Ghat'},
            
            # Food & Water
            {'name': 'Food Court Main', 'category': 'food', 'latitude': 29.9500, 'longitude': 78.1600, 'description': 'Multiple food options'},
            {'name': 'Water Point 1', 'category': 'food', 'latitude': 29.9576, 'longitude': 78.1712, 'description': 'Drinking water available'},
            {'name': 'Water Point 2', 'category': 'food', 'latitude': 29.9650, 'longitude': 78.1850, 'description': 'Drinking water available'},
            {'name': 'Langar Hall', 'category': 'food', 'latitude': 29.9400, 'longitude': 78.1400, 'description': 'Free community kitchen'},
            
            # Restrooms
            {'name': 'Public Toilet 1', 'category': 'restroom', 'latitude': 29.9576, 'longitude': 78.1712, 'description': 'Near Har Ki Pauri'},
            {'name': 'Public Toilet 2', 'category': 'restroom', 'latitude': 29.9350, 'longitude': 78.1550, 'description': 'Near Triveni Ghat'},
            {'name': 'Public Toilet 3', 'category': 'restroom', 'latitude': 29.9650, 'longitude': 78.1850, 'description': 'Near Ram Jhula'},
            
            # Parking
            {'name': 'Parking Lot A', 'category': 'parking', 'latitude': 29.9400, 'longitude': 78.1400, 'description': 'Car parking available'},
            {'name': 'Parking Lot B', 'category': 'parking', 'latitude': 29.9500, 'longitude': 78.1500, 'description': 'Two-wheeler parking'},
            {'name': 'Parking Lot C', 'category': 'parking', 'latitude': 29.9800, 'longitude': 78.1900, 'description': 'Bus parking'},
            
            # Accommodation
            {'name': 'Hotel Ganga View', 'category': 'accommodation', 'latitude': 29.9576, 'longitude': 78.1712, 'description': '3-star hotel', 'phone': '+91-9876543210'},
            {'name': 'Dharamshala 1', 'category': 'accommodation', 'latitude': 29.9350, 'longitude': 78.1550, 'description': 'Budget accommodation'},
            {'name': 'Guest House', 'category': 'accommodation', 'latitude': 29.9500, 'longitude': 78.1600, 'description': 'Family rooms available'},
            
            # Transport
            {'name': 'Bus Stand', 'category': 'transport', 'latitude': 29.9400, 'longitude': 78.1400, 'description': 'Main bus terminal'},
            {'name': 'Auto Stand', 'category': 'transport', 'latitude': 29.9576, 'longitude': 78.1712, 'description': 'Auto rickshaw stand'},
            {'name': 'Taxi Stand', 'category': 'transport', 'latitude': 29.9500, 'longitude': 78.1600, 'description': 'Taxi booking'},
            
            # Worship
            {'name': 'Har Ki Pauri', 'category': 'worship', 'latitude': 29.9576, 'longitude': 78.1712, 'description': 'Main ghat for prayers'},
            {'name': 'Triveni Ghat', 'category': 'worship', 'latitude': 29.9350, 'longitude': 78.1550, 'description': 'Sacred bathing ghat'},
            {'name': 'Mansa Devi Temple', 'category': 'worship', 'latitude': 29.9650, 'longitude': 78.1850, 'description': 'Famous temple'},
            
            # Shopping
            {'name': 'Main Bazaar', 'category': 'shopping', 'latitude': 29.9500, 'longitude': 78.1600, 'description': 'Shopping market'},
            {'name': 'Gift Shop 1', 'category': 'shopping', 'latitude': 29.9576, 'longitude': 78.1712, 'description': 'Religious items'},
            {'name': 'Gift Shop 2', 'category': 'shopping', 'latitude': 29.9350, 'longitude': 78.1550, 'description': 'Souvenirs'},
        ]
        
        for amenity_data in amenities_data:
            amenity, created = Amenity.objects.get_or_create(
                name=amenity_data['name'],
                defaults=amenity_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created amenity: {amenity.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Amenity already exists: {amenity.name}'))

        self.stdout.write(self.style.SUCCESS('\nInitial data loaded successfully!'))

