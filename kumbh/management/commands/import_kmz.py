"""
Management command to import KMZ/KML files into GeographicFeature model
Usage: python manage.py import_kmz <kmz_file_path> [--feature-type=<type>]
"""
import zipfile
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from kumbh.models import GeographicFeature
import os


class Command(BaseCommand):
    help = 'Import geographic features from KMZ/KML files'

    def add_arguments(self, parser):
        parser.add_argument('kmz_file', type=str, help='Path to KMZ file')
        parser.add_argument(
            '--feature-type',
            type=str,
            default='other',
            choices=['road', 'area', 'zone', 'parking', 'holding_area', 'staging_area', 'release_point', 'route', 'other'],
            help='Type of feature to assign to imported data'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing features from the same KMZ file before importing'
        )

    def handle(self, *args, **options):
        kmz_file = options['kmz_file']
        feature_type = options['feature_type']
        clear_existing = options['clear_existing']

        if not os.path.exists(kmz_file):
            raise CommandError(f'KMZ file not found: {kmz_file}')

        kmz_file_name = os.path.basename(kmz_file)

        # Clear existing features from this file if requested
        if clear_existing:
            deleted_count = GeographicFeature.objects.filter(kmz_file_name=kmz_file_name).delete()[0]
            self.stdout.write(self.style.WARNING(f'Deleted {deleted_count} existing features from {kmz_file_name}'))

        try:
            # Extract and parse KMZ
            with zipfile.ZipFile(kmz_file, 'r') as zip_ref:
                # Find the KML file (usually doc.kml)
                kml_files = [f for f in zip_ref.namelist() if f.endswith('.kml')]
                if not kml_files:
                    raise CommandError('No KML file found in KMZ archive')
                
                kml_file = kml_files[0]
                kml_content = zip_ref.read(kml_file)
                
                # Parse KML
                root = ET.fromstring(kml_content)
                
                # Define KML namespace
                ns = {'kml': 'http://www.opengis.net/kml/2.2'}
                
                imported_count = 0
                
                with transaction.atomic():
                    # Find all Placemarks
                    placemarks = root.findall('.//kml:Placemark', ns)
                    
                    if not placemarks:
                        self.stdout.write(self.style.WARNING('No Placemarks found in KML file'))
                        return
                    
                    for placemark in placemarks:
                        # Get name
                        name_elem = placemark.find('kml:name', ns)
                        name = name_elem.text if name_elem is not None and name_elem.text else 'Unnamed Feature'
                        
                        # Get description
                        desc_elem = placemark.find('kml:description', ns)
                        description = desc_elem.text if desc_elem is not None and desc_elem.text else None
                        
                        # Determine geometry type and extract coordinates
                        geometry_type = None
                        latitude = None
                        longitude = None
                        coordinates = None
                        
                        # Check for Point
                        point = placemark.find('.//kml:Point', ns)
                        if point is not None:
                            geometry_type = 'point'
                            coord_elem = point.find('kml:coordinates', ns)
                            if coord_elem is not None and coord_elem.text:
                                coords = coord_elem.text.strip().split(',')
                                if len(coords) >= 2:
                                    longitude = float(coords[0])
                                    latitude = float(coords[1])
                        
                        # Check for LineString
                        linestring = placemark.find('.//kml:LineString', ns)
                        if linestring is not None:
                            geometry_type = 'line'
                            coord_elem = linestring.find('kml:coordinates', ns)
                            if coord_elem is not None and coord_elem.text:
                                coords_list = []
                                for coord_str in coord_elem.text.strip().split():
                                    parts = coord_str.split(',')
                                    if len(parts) >= 2:
                                        coords_list.append([float(parts[1]), float(parts[0])])  # lat, lng
                                if coords_list:
                                    coordinates = coords_list
                                    # Calculate center point for reference
                                    lats = [c[0] for c in coords_list]
                                    lngs = [c[1] for c in coords_list]
                                    latitude = sum(lats) / len(lats)
                                    longitude = sum(lngs) / len(lngs)
                        
                        # Check for Polygon
                        polygon = placemark.find('.//kml:Polygon', ns)
                        if polygon is not None:
                            geometry_type = 'polygon'
                            outer_boundary = polygon.find('.//kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', ns)
                            if outer_boundary is not None and outer_boundary.text:
                                coords_list = []
                                for coord_str in outer_boundary.text.strip().split():
                                    parts = coord_str.split(',')
                                    if len(parts) >= 2:
                                        coords_list.append([float(parts[1]), float(parts[0])])  # lat, lng
                                if coords_list:
                                    coordinates = coords_list
                                    # Calculate center point
                                    lats = [c[0] for c in coords_list]
                                    lngs = [c[1] for c in coords_list]
                                    latitude = sum(lats) / len(lats)
                                    longitude = sum(lngs) / len(lngs)
                        
                        # Only create if we have valid geometry
                        if geometry_type:
                            # Auto-detect feature type from name/file name
                            detected_type = self._detect_feature_type(name, kmz_file_name)
                            final_feature_type = detected_type if detected_type != 'other' else feature_type
                            
                            feature, created = GeographicFeature.objects.get_or_create(
                                name=name,
                                kmz_file_name=kmz_file_name,
                                defaults={
                                    'feature_type': final_feature_type,
                                    'geometry_type': geometry_type,
                                    'latitude': latitude,
                                    'longitude': longitude,
                                    'coordinates': coordinates,
                                    'description': description,
                                }
                            )
                            
                            if created:
                                imported_count += 1
                            else:
                                # Update existing feature
                                feature.feature_type = final_feature_type
                                feature.geometry_type = geometry_type
                                feature.latitude = latitude
                                feature.longitude = longitude
                                feature.coordinates = coordinates
                                feature.description = description
                                feature.save()
                                imported_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully imported {imported_count} features from {kmz_file_name}'
                    )
                )
                
        except Exception as e:
            raise CommandError(f'Error processing KMZ file: {str(e)}')

    def _detect_feature_type(self, name, file_name):
        """Auto-detect feature type from name or file name"""
        name_lower = name.lower()
        file_lower = file_name.lower()
        
        if 'road' in name_lower or 'road' in file_lower:
            return 'road'
        elif 'parking' in name_lower or 'parking' in file_lower:
            return 'parking'
        elif 'holding' in name_lower or 'holding' in file_lower:
            return 'holding_area'
        elif 'staging' in name_lower or 'staging' in file_lower:
            return 'staging_area'
        elif 'release' in name_lower or 'release' in file_lower:
            return 'release_point'
        elif 'route' in name_lower or 'route' in file_lower:
            return 'route'
        # Don't auto-detect as 'zone' - zones should be managed separately via Zone model
        # If file is named "Inner" or "Outer", treat as 'area' instead
        elif 'inner' in file_lower or 'outer' in file_lower:
            return 'area'
        elif 'area' in name_lower or 'area' in file_lower:
            return 'area'
        else:
            return 'other'

