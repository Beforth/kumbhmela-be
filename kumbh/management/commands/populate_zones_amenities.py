"""
Management command to populate Zone and Amenity models from GeographicFeature objects
Usage: python manage.py populate_zones_amenities [--dry-run]
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from kumbh.models import GeographicFeature, Zone, Amenity
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate Zone and Amenity models from GeographicFeature objects'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating records'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip features that already have corresponding Zone/Amenity objects'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        skip_existing = options['skip_existing']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        zones_created = 0
        zones_updated = 0
        amenities_created = 0
        amenities_updated = 0
        skipped = 0

        try:
            with transaction.atomic():
                # Process zones and areas
                zone_features = GeographicFeature.objects.filter(
                    feature_type__in=['zone', 'area'],
                    is_active=True
                )

                self.stdout.write(f'\nProcessing {zone_features.count()} zone/area features...')

                for feature in zone_features:
                    # Check if zone already exists with same name
                    existing_zone = Zone.objects.filter(name=feature.name, is_active=True).first()
                    
                    if existing_zone and skip_existing:
                        self.stdout.write(f'  Skipping {feature.name} (already exists)')
                        skipped += 1
                        continue

                    zone_data = {
                        'name': feature.name,
                        'status': 'safe',  # Default status
                        'color': 'green',  # Default color
                        'capacity': 25,  # Default capacity
                        'description': '',  # Empty description
                        'is_active': True,
                    }

                    # Determine zone type and set coordinates
                    if feature.geometry_type == 'point' and feature.latitude and feature.longitude:
                        zone_data['zone_type'] = 'circle'
                        zone_data['latitude'] = Decimal(str(feature.latitude))
                        zone_data['longitude'] = Decimal(str(feature.longitude))
                    elif feature.geometry_type == 'polygon' and feature.coordinates:
                        zone_data['zone_type'] = 'polygon'
                        zone_data['polygon'] = feature.coordinates
                        # Calculate center point for reference
                        if feature.coordinates and len(feature.coordinates) > 0:
                            lats = [c[0] for c in feature.coordinates if isinstance(c, list) and len(c) >= 2]
                            lngs = [c[1] for c in feature.coordinates if isinstance(c, list) and len(c) >= 2]
                            if lats and lngs:
                                zone_data['latitude'] = Decimal(str(sum(lats) / len(lats)))
                                zone_data['longitude'] = Decimal(str(sum(lngs) / len(lngs)))
                    elif feature.latitude and feature.longitude:
                        # Has coordinates but geometry type might be missing
                        zone_data['zone_type'] = 'circle'
                        zone_data['latitude'] = Decimal(str(feature.latitude))
                        zone_data['longitude'] = Decimal(str(feature.longitude))
                    else:
                        # No coordinates - skip or create without coordinates
                        self.stdout.write(
                            self.style.WARNING(f'  Skipping {feature.name} - no coordinates')
                        )
                        skipped += 1
                        continue

                    if existing_zone:
                        # Update existing zone
                        if not dry_run:
                            for key, value in zone_data.items():
                                setattr(existing_zone, key, value)
                            existing_zone.save()
                        zones_updated += 1
                        self.stdout.write(f'  Updated zone: {feature.name}')
                    else:
                        # Create new zone
                        if not dry_run:
                            Zone.objects.create(**zone_data)
                        zones_created += 1
                        self.stdout.write(f'  Created zone: {feature.name}')

                # Process amenities (parking, and other features that could be amenities)
                amenity_features = GeographicFeature.objects.filter(
                    feature_type__in=['parking', 'other'],
                    is_active=True
                )

                # Also check for features that might be amenities based on name
                potential_amenities = GeographicFeature.objects.filter(
                    is_active=True
                ).exclude(feature_type__in=['zone', 'area', 'road', 'route', 'holding_area', 'staging_area', 'release_point'])

                all_amenity_features = (amenity_features | potential_amenities).distinct()

                self.stdout.write(f'\nProcessing {all_amenity_features.count()} potential amenity features...')

                # Map feature types/names to amenity categories
                def detect_amenity_category(feature):
                    name_lower = feature.name.lower()
                    feature_type = feature.feature_type.lower()

                    if 'toilet' in name_lower or 'restroom' in name_lower or 'washroom' in name_lower:
                        return 'restroom'
                    elif 'medical' in name_lower or 'hospital' in name_lower or 'clinic' in name_lower:
                        return 'medical'
                    elif 'food' in name_lower or 'water' in name_lower or 'drinking' in name_lower:
                        return 'food'
                    elif 'parking' in name_lower or feature_type == 'parking':
                        return 'parking'
                    elif 'accommodation' in name_lower or 'hotel' in name_lower or 'lodge' in name_lower:
                        return 'accommodation'
                    elif 'transport' in name_lower or 'bus' in name_lower or 'station' in name_lower:
                        return 'transport'
                    elif 'temple' in name_lower or 'mandir' in name_lower or 'worship' in name_lower:
                        return 'worship'
                    elif 'shop' in name_lower or 'market' in name_lower or 'store' in name_lower:
                        return 'shopping'
                    else:
                        return 'other'

                for feature in all_amenity_features:
                    # Check if amenity already exists with same name
                    existing_amenity = Amenity.objects.filter(name=feature.name, is_active=True).first()
                    
                    if existing_amenity and skip_existing:
                        self.stdout.write(f'  Skipping {feature.name} (already exists)')
                        skipped += 1
                        continue

                    # Need coordinates for amenities
                    if not feature.latitude or not feature.longitude:
                        # Try to get from coordinates if it's a polygon/line
                        if feature.coordinates and len(feature.coordinates) > 0:
                            coords = feature.coordinates[0]
                            if isinstance(coords, list) and len(coords) >= 2:
                                feature.latitude = Decimal(str(coords[0]))
                                feature.longitude = Decimal(str(coords[1]))
                            else:
                                self.stdout.write(
                                    self.style.WARNING(f'  Skipping {feature.name} - no coordinates')
                                )
                                skipped += 1
                                continue
                        else:
                            self.stdout.write(
                                self.style.WARNING(f'  Skipping {feature.name} - no coordinates')
                            )
                            skipped += 1
                            continue

                    category = detect_amenity_category(feature)

                    amenity_data = {
                        'name': feature.name,
                        'category': category,
                        'latitude': Decimal(str(feature.latitude)),
                        'longitude': Decimal(str(feature.longitude)),
                        'description': '',  # Empty description
                        'is_active': True,
                    }

                    if existing_amenity:
                        # Update existing amenity
                        if not dry_run:
                            for key, value in amenity_data.items():
                                setattr(existing_amenity, key, value)
                            existing_amenity.save()
                        amenities_updated += 1
                        self.stdout.write(f'  Updated amenity: {feature.name} ({category})')
                    else:
                        # Create new amenity
                        if not dry_run:
                            Amenity.objects.create(**amenity_data)
                        amenities_created += 1
                        self.stdout.write(f'  Created amenity: {feature.name} ({category})')

                if dry_run:
                    # Rollback transaction in dry-run mode
                    transaction.set_rollback(True)

            self.stdout.write(self.style.SUCCESS('\n' + '='*60))
            self.stdout.write(self.style.SUCCESS('Summary:'))
            self.stdout.write(self.style.SUCCESS(f'  Zones created: {zones_created}'))
            self.stdout.write(self.style.SUCCESS(f'  Zones updated: {zones_updated}'))
            self.stdout.write(self.style.SUCCESS(f'  Amenities created: {amenities_created}'))
            self.stdout.write(self.style.SUCCESS(f'  Amenities updated: {amenities_updated}'))
            self.stdout.write(self.style.SUCCESS(f'  Skipped: {skipped}'))
            if dry_run:
                self.stdout.write(self.style.WARNING('\nThis was a DRY RUN - no changes were made'))
            else:
                self.stdout.write(self.style.SUCCESS('\nSuccessfully populated zones and amenities!'))

        except Exception as e:
            raise CommandError(f'Error processing features: {str(e)}')

