"""
Arduino RC Car Controller
Python interface for controlling the RC car via serial communication
"""

import serial
import time
from typing import Optional


class RCCarController:
    """Controller for RC car with single drive motor and servo steering"""
    
    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 115200):
        """
        Initialize RC Car Controller
        
        Args:
            port: Serial port (e.g., '/dev/ttyUSB0' on Linux, 'COM3' on Windows)
            baudrate: Serial communication baud rate (default: 115200)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial: Optional[serial.Serial] = None
        self.is_connected = False
        self.current_speed = 0
        self.current_steering = 90  # Center
        
    def connect(self):
        """Establish serial connection to Arduino"""
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to initialize
            self.is_connected = True
            print(f"Connected to RC car on {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Error connecting to {self.port}: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.is_connected and self.serial:
            self.stop()
            self.center_steering()
            self.serial.close()
            self.is_connected = False
            print("Disconnected from RC car")
    
    def _send_command(self, command: str):
        """Send command to Arduino via serial"""
        if not self.is_connected or not self.serial:
            raise RuntimeError("Not connected to RC car. Call connect() first.")
        
        self.serial.write(f'{command}\n'.encode())
        time.sleep(0.05)  # Small delay for command processing
    
    def forward(self, speed: int = 200):
        """
        Move forward at specified speed
        
        Args:
            speed: Speed value (0-255, default: 200)
        """
        speed = max(0, min(255, speed))  # Constrain to valid range
        self._send_command(f'F{speed}')
        self.current_speed = speed
    
    def backward(self, speed: int = 200):
        """
        Move backward at specified speed
        
        Args:
            speed: Speed value (0-255, default: 200)
        """
        speed = max(0, min(255, speed))  # Constrain to valid range
        self._send_command(f'B{speed}')
        self.current_speed = -speed
    
    def stop(self):
        """Stop the drive motor"""
        self._send_command('S')
        self.current_speed = 0
    
    def set_steering(self, angle: int):
        """
        Set steering angle
        
        Args:
            angle: Steering angle (0-180, 90=center, <90=left, >90=right)
        """
        angle = max(0, min(180, angle))  # Constrain to 0-180
        self._send_command(f'ST{angle}')
        self.current_steering = angle
    
    def turn_left(self, angle_offset: int = 30):
        """
        Turn left by specified degrees from center
        
        Args:
            angle_offset: Degrees to turn left from center (0-45, default: 30)
        """
        angle_offset = max(0, min(45, angle_offset))
        self._send_command(f'L{angle_offset}')
        self.current_steering = 90 - angle_offset
    
    def turn_right(self, angle_offset: int = 30):
        """
        Turn right by specified degrees from center
        
        Args:
            angle_offset: Degrees to turn right from center (0-45, default: 30)
        """
        angle_offset = max(0, min(45, angle_offset))
        self._send_command(f'R{angle_offset}')
        self.current_steering = 90 + angle_offset
    
    def center_steering(self):
        """Center the steering"""
        self.set_steering(90)
    
    def move_forward_with_steering(self, speed: int = 200, steering_angle: int = 90, duration: float = 1.0):
        """
        Move forward with steering for specified duration
        
        Args:
            speed: Speed value (0-255)
            steering_angle: Steering angle (0-180, 90=center)
            duration: Duration in seconds
        """
        self.set_steering(steering_angle)
        self.forward(speed)
        time.sleep(duration)
        self.stop()
    
    def execute_maneuver(self, maneuver: str, speed: int = 200, duration: float = 1.0):
        """
        Execute a predefined maneuver
        
        Args:
            maneuver: Maneuver type ('forward', 'backward', 'left', 'right', 'stop')
            speed: Speed value (0-255)
            duration: Duration in seconds
        """
        maneuver = maneuver.lower()
        
        if maneuver == 'forward':
            self.forward(speed)
            time.sleep(duration)
            self.stop()
        elif maneuver == 'backward':
            self.backward(speed)
            time.sleep(duration)
            self.stop()
        elif maneuver == 'left':
            self.turn_left(30)
            self.forward(speed)
            time.sleep(duration)
            self.stop()
            self.center_steering()
        elif maneuver == 'right':
            self.turn_right(30)
            self.forward(speed)
            time.sleep(duration)
            self.stop()
            self.center_steering()
        elif maneuver == 'stop':
            self.stop()
        else:
            print(f"Unknown maneuver: {maneuver}")
    
    def get_status(self) -> dict:
        """Get current status of the RC car"""
        return {
            'connected': self.is_connected,
            'speed': self.current_speed,
            'steering': self.current_steering
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


# Example usage and testing
if __name__ == '__main__':
    # Determine the correct port for your system
    # Linux/Mac: /dev/ttyUSB0, /dev/ttyACM0
    # Windows: COM3, COM4, etc.
    
    port = '/dev/ttyUSB0'  # Change this to your actual port
    
    # Use context manager for automatic cleanup
    with RCCarController(port) as car:
        if car.is_connected:
            print("Testing RC Car Controller...")
            
            # Test forward
            print("Moving forward...")
            car.forward(200)
            time.sleep(2)
            car.stop()
            
            # Test steering
            print("Testing steering...")
            car.set_steering(45)  # Turn left
            time.sleep(1)
            car.set_steering(135)  # Turn right
            time.sleep(1)
            car.center_steering()
            
            # Test backward
            print("Moving backward...")
            car.backward(150)
            time.sleep(2)
            car.stop()
            
            # Test maneuvers
            print("Testing maneuvers...")
            car.execute_maneuver('forward', speed=180, duration=1.5)
            car.execute_maneuver('left', speed=150, duration=1.0)
            car.execute_maneuver('right', speed=150, duration=1.0)
            
            # Print status
            print("Status:", car.get_status())
            print("Test complete!")

