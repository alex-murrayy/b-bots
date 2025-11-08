#!/usr/bin/env python3
"""
Update Campus Map with Real GPS Coordinates
Updates the map to use real GPS coordinates instead of relative coordinates
"""

from map import CampusMap
from gps_integration import UB_BUILDINGS_GPS


def update_map_with_gps_coordinates(campus_map: CampusMap):
    """Update map locations with real GPS coordinates"""
    
    print("Updating map with real GPS coordinates...")
    updated_count = 0
    
    for building_name, (lat, lon) in UB_BUILDINGS_GPS.items():
        location = campus_map.get_location(building_name)
        if location:
            # Update coordinates with real GPS
            location.coordinates = (lat, lon)
            updated_count += 1
            print(f"  ✓ Updated {building_name}: ({lat}, {lon})")
        else:
            print(f"  ✗ Building not found: {building_name}")
    
    print(f"\nUpdated {updated_count} locations with GPS coordinates")
    return updated_count


def create_gps_enabled_map() -> CampusMap:
    """Create a new map instance with GPS coordinates"""
    campus_map = CampusMap()
    update_map_with_gps_coordinates(campus_map)
    return campus_map


if __name__ == '__main__':
    # Test the GPS coordinate update
    print("=" * 60)
    print("UB Campus Map - GPS Coordinates Update")
    print("=" * 60)
    print()
    
    campus_map = CampusMap()
    update_map_with_gps_coordinates(campus_map)
    
    print("\n" + "=" * 60)
    print("Sample Locations:")
    print("=" * 60)
    
    sample_locations = ["Capen Hall", "Norton Hall", "Student Union", "Ellicott Complex"]
    for name in sample_locations:
        loc = campus_map.get_location(name)
        if loc:
            lat, lon = loc.coordinates
            print(f"{name:25} Lat: {lat:.6f}, Lon: {lon:.6f}")
    
    print("\nMap updated successfully!")

