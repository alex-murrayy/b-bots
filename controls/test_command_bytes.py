#!/usr/bin/env python3
"""
Test script to verify exact bytes being sent to Arduino
This helps diagnose command mapping issues
"""

import sys
import time
import argparse

try:
    from arduino_wasd_controller import ArduinoWASDController
except ImportError:
    print("Error: Could not import arduino_wasd_controller")
    sys.exit(1)


def test_command_bytes(port: str = '/dev/ttyACM0', baudrate: int = 9600):
    """Test that correct bytes are sent for each command"""
    print("=" * 70)
    print("COMMAND BYTE VERIFICATION TEST")
    print("=" * 70)
    print(f"Port: {port}")
    print(f"Baudrate: {baudrate}")
    print()
    
    controller = ArduinoWASDController(port=port, baudrate=baudrate, debug=True)
    
    if not controller.connect(debug=True):
        print("FAILED: Could not connect")
        sys.exit(1)
    
    # Wait for Arduino to be ready
    time.sleep(1)
    
    # Test each command and verify byte sent
    commands = [
        ('forward', 'w', 0x77),
        ('backward', 's', 0x73),
        ('left', 'a', 0x61),
        ('right', 'd', 0x64),
        ('stop', ' ', 0x20),
        ('all_off', 'x', 0x78),
    ]
    
    print("\n" + "=" * 70)
    print("TESTING COMMANDS")
    print("=" * 70)
    
    for name, char, expected_byte in commands:
        print(f"\n--- Testing {name} (should send '{char}' = 0x{expected_byte:02x}) ---")
        
        # Get the method
        method = getattr(controller, name)
        
        # Send command with debug
        try:
            response = method(debug=True)
            print(f"Response: {response}")
        except Exception as e:
            print(f"ERROR: {e}")
        
        time.sleep(0.5)
    
    controller.disconnect()
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\nCheck the DEBUG output above to verify:")
    print("1. Each method sends the correct character")
    print("2. Each character is encoded to the correct byte value")
    print("3. Arduino responds with the expected response")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test command byte encoding')
    parser.add_argument('--port', '-p', default='/dev/ttyACM0',
                       help='Serial port')
    parser.add_argument('--baudrate', '-b', type=int, default=9600,
                       help='Baud rate')
    
    args = parser.parse_args()
    test_command_bytes(port=args.port, baudrate=args.baudrate)

