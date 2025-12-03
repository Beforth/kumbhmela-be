from django.core.management.base import BaseCommand
from kumbh.models import Zone
import json


class Command(BaseCommand):
    help = 'Populate polygon data for existing zones'

    def handle(self, *args, **options):
        # Define polygons for each zone (approximate areas around their center points)
        # Format: [[lat1, lng1], [lat2, lng2], [lat3, lng3], [lat4, lng4], [lat1, lng1]]
        # Creating rectangular polygons around each zone center
        
        zone_polygons = {
            'Har Ki Pauri': [
                [29.9576, 78.1712],  # Center
                [29.9590, 78.1725],  # NE
                [29.9585, 78.1740],  # E
                [29.9565, 78.1735],  # SE
                [29.9555, 78.1720],  # S
                [29.9560, 78.1700],  # SW
                [29.9570, 78.1695],  # W
                [29.9585, 78.1700],  # NW
                [29.9576, 78.1712],  # Back to start
            ],
            'Triveni Ghat': [
                [29.9350, 78.1550],  # Center
                [29.9365, 78.1565],  # NE
                [29.9360, 78.1580],  # E
                [29.9340, 78.1575],  # SE
                [29.9330, 78.1560],  # S
                [29.9335, 78.1540],  # SW
                [29.9345, 78.1535],  # W
                [29.9360, 78.1540],  # NW
                [29.9350, 78.1550],  # Back to start
            ],
            'Main Bazaar': [
                [29.9500, 78.1600],  # Center
                [29.9515, 78.1615],  # NE
                [29.9510, 78.1630],  # E
                [29.9490, 78.1625],  # SE
                [29.9480, 78.1610],  # S
                [29.9485, 78.1590],  # SW
                [29.9495, 78.1585],  # W
                [29.9510, 78.1590],  # NW
                [29.9500, 78.1600],  # Back to start
            ],
            'Ram Jhula': [
                [29.9650, 78.1850],  # Center
                [29.9665, 78.1865],  # NE
                [29.9660, 78.1880],  # E
                [29.9640, 78.1875],  # SE
                [29.9630, 78.1860],  # S
                [29.9635, 78.1840],  # SW
                [29.9645, 78.1835],  # W
                [29.9660, 78.1840],  # NW
                [29.9650, 78.1850],  # Back to start
            ],
            'Lakshman Jhula': [
                [29.9800, 78.1900],  # Center
                [29.9815, 78.1915],  # NE
                [29.9810, 78.1930],  # E
                [29.9790, 78.1925],  # SE
                [29.9780, 78.1910],  # S
                [29.9785, 78.1890],  # SW
                [29.9795, 78.1885],  # W
                [29.9810, 78.1890],  # NW
                [29.9800, 78.1900],  # Back to start
            ],
            'Bharat Mandir': [
                [29.9400, 78.1400],  # Center
                [29.9415, 78.1415],  # NE
                [29.9410, 78.1430],  # E
                [29.9390, 78.1425],  # SE
                [29.9380, 78.1410],  # S
                [29.9385, 78.1390],  # SW
                [29.9395, 78.1385],  # W
                [29.9410, 78.1390],  # NW
                [29.9400, 78.1400],  # Back to start
            ],
        }
        
        updated_count = 0
        for zone_name, polygon in zone_polygons.items():
            try:
                zone = Zone.objects.get(name=zone_name)
                zone.polygon = polygon
                zone.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Updated {zone_name} with polygon ({len(polygon)} points)')
                )
            except Zone.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Zone "{zone_name}" not found')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Successfully updated {updated_count} zones with polygon data')
        )

