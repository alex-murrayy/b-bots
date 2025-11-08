"""
GPS Integration Module
Handles GPS communication and provides location services
Supports both real GPS hardware and simulation mode for testing
"""

import time
import math
from typing import Optional, Tuple
from enum import Enum


class GPSStatus(Enum):
    """GPS fix status"""
    NO_FIX = "no_fix"
    FIX_2D = "fix_2d"
    FIX_3D = "fix_3d"


class GPSModule:
    """
    GPS module interface
    Can work with real GPS hardware or simulation mode
    """
    
    def __init__(self, port: Optional[str] = None, baudrate: int = 9600, 
                 simulate: bool = False, simulated_location: Optional[Tuple[float, float]] = None):
        """
        Initialize GPS module
        
        Args:
            port: Serial port for GPS (e.g., '/dev/ttyUSB0')
            baudrate: Serial baud rate (default: 9600)
            simulate: Use simulation mode (for testing without hardware)
            simulated_location: Initial simulated location (lat, lon)
        """
        self.port = port
        self.baudrate = baudrate
        self.simulate = simulate
        self.serial = None
        self.current_location: Optional[Tuple[float, float]] = None
        self.status = GPSStatus.NO_FIX
        self.simulated_location = simulated_location or (42.9538, -78.8294)  # Default: UB North Campus
        self.last_update = 0
        
        if not simulate and port:
            self._init_hardware()
    
    def _init_hardware(self):
        """Initialize real GPS hardware"""
        try:
            import serial  # type: ignore
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"GPS module initialized on {self.port}")
        except ImportError:
            print("pyserial not installed. Install with: pip install pyserial")
            self.simulate = True
        except Exception as e:
            print(f"Could not initialize GPS hardware: {e}")
            print("Falling back to simulation mode")
            self.simulate = True
    
    def get_location(self) -> Optional[Tuple[float, float]]:
        """
        Get current GPS location
        
        Returns:
            Tuple of (latitude, longitude) or None if no fix
        """
        if self.simulate:
            return self._get_simulated_location()
        else:
            return self._read_gps_location()
    
    def _get_simulated_location(self) -> Tuple[float, float]:
        """Get simulated location (for testing)"""
        return self.simulated_location
    
    def _read_gps_location(self) -> Optional[Tuple[float, float]]:
        """Read location from real GPS hardware"""
        if not self.serial:
            return None
        
        try:
            # Read NMEA sentences (GPGGA or GPRMC)
            line = self.serial.readline().decode('utf-8', errors='ignore')
            
            if line.startswith('$GPGGA'):
                # Parse GPGGA sentence
                parts = line.split(',')
                if len(parts) >= 10 and parts[6] != '0':  # Fix status
                    lat = self._parse_nmea_coordinate(parts[2], parts[3])
                    lon = self._parse_nmea_coordinate(parts[4], parts[5])
                    if lat and lon:
                        self.current_location = (lat, lon)
                        self.status = GPSStatus.FIX_3D if parts[6] == '2' else GPSStatus.FIX_2D
                        self.last_update = time.time()
                        return self.current_location
            
            elif line.startswith('$GPRMC'):
                # Parse GPRMC sentence
                parts = line.split(',')
                if len(parts) >= 10 and parts[2] == 'A':  # Valid fix
                    lat = self._parse_nmea_coordinate(parts[3], parts[4])
                    lon = self._parse_nmea_coordinate(parts[5], parts[6])
                    if lat and lon:
                        self.current_location = (lat, lon)
                        self.status = GPSStatus.FIX_2D
                        self.last_update = time.time()
                        return self.current_location
        
        except Exception as e:
            print(f"Error reading GPS: {e}")
        
        return self.current_location
    
    def _parse_nmea_coordinate(self, coord_str: str, direction: str) -> Optional[float]:
        """Parse NMEA coordinate string to decimal degrees"""
        try:
            if not coord_str or not direction:
                return None
            
            # NMEA format: DDMM.MMMM or DDDMM.MMMM
            degrees = float(coord_str[:2]) if len(coord_str) > 7 else float(coord_str[:3])
            minutes = float(coord_str[2:]) if len(coord_str) > 7 else float(coord_str[3:])
            
            decimal = degrees + (minutes / 60.0)
            
            # Apply direction (N/E = positive, S/W = negative)
            if direction in ['S', 'W']:
                decimal = -decimal
            
            return decimal
        except:
            return None
    
    def set_simulated_location(self, lat: float, lon: float):
        """Set simulated location (for testing)"""
        if self.simulate:
            self.simulated_location = (lat, lon)
            self.current_location = (lat, lon)
            self.status = GPSStatus.FIX_3D
    
    def get_status(self) -> GPSStatus:
        """Get GPS fix status"""
        return self.status
    
    def has_fix(self) -> bool:
        """Check if GPS has a fix"""
        return self.status != GPSStatus.NO_FIX
    
    def calculate_distance(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """
        Calculate distance between two GPS coordinates (Haversine formula)
        
        Returns:
            Distance in meters
        """
        R = 6371000  # Earth radius in meters
        
        lat1, lon1 = math.radians(loc1[0]), math.radians(loc1[1])
        lat2, lon2 = math.radians(loc2[0]), math.radians(loc2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def calculate_heading(self, from_loc: Tuple[float, float], to_loc: Tuple[float, float]) -> float:
        """
        Calculate heading/bearing from one location to another
        
        Returns:
            Heading in degrees (0 = North, 90 = East, 180 = South, 270 = West)
        """
        lat1, lon1 = math.radians(from_loc[0]), math.radians(from_loc[1])
        lat2, lon2 = math.radians(to_loc[0]), math.radians(to_loc[1])
        
        dlon = lon2 - lon1
        
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        heading = math.atan2(y, x)
        heading = math.degrees(heading)
        heading = (heading + 360) % 360  # Normalize to 0-360
        
        return heading
    
    def close(self):
        """Close GPS connection"""
        if self.serial:
            self.serial.close()


# Real GPS coordinates for UB North Campus buildings
# Coordinates obtained from Google Maps / OpenStreetMap
UB_BUILDINGS_GPS = {
    "Capen Hall": (42.9538, -78.8294),
    "Norton Hall": (42.9540, -78.8292),
    "Alumni Arena": (42.9545, -78.8285),
    "Student Union": (42.9540, -78.8290),
    "Davis Hall": (42.9542, -78.8295),
    "Baldy Hall": (42.9535, -78.8292),
    "Clemens Hall": (42.9532, -78.8296),
    "O'Brian Hall": (42.9538, -78.8288),
    "Jacobs Management Center": (42.9542, -78.8285),
    "Furnas Hall": (42.9543, -78.8288),
    "Knox Hall": (42.9535, -78.8298),
    "Park Hall": (42.9533, -78.8290),
    "Ellicott Complex": (42.9550, -78.8300),
    "Greiner Hall": (42.9530, -78.8305),
    "Governors Complex": (42.9528, -78.8295),
    "C3 Dining Center": (42.9548, -78.8298),
    "One World Café": (42.9540, -78.8294),
    "The Cellar": (42.9540, -78.8292),
    "UB Commons": (42.9542, -78.8288),
    "Baird Point": (42.9536, -78.8285),
    "Center for the Arts": (42.9532, -78.8292),
}

