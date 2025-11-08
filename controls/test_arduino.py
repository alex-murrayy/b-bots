#!/usr/bin/env python3
"""
Simple test script to verify Arduino connection and commands
"""

import sys
import time

try:
    from arduino_wasd_controller import ArduinoWASDController
except ImportError:
    print("Error: Could not import arduino_wasd_controller")
    print("Make sure you're running from the controls directory")
    sys.exit(1)

def test_arduino():
    """Test Arduino connection and basic commands"""
    port = '/dev/ttyACM0'
    
    print(f"Testing Arduino connection on {port}...")
    print("=" * 60)
    
    controller = ArduinoWASDController(port=port)
    
    if not controller.connect():
        print("FAILED: Could not connect to Arduino")
        print("\nTroubleshooting:")
        print("1. Check Arduino is connected via USB")
        print("2. Check port: python3 -m serial.tools.list_ports")
        print("3. Check permissions: sudo usermod -a -G dialout $USER")
        sys.exit(1)
    
    print("SUCCESS: Connected to Arduino")
    print("\nTesting commands...")
    print("=" * 60)
    
    # Test forward
    print("Test 1: Forward (W)")
    response = controller.forward()
    print(f"Response: {response}")
    time.sleep(1)
    
    # Test stop
    print("\nTest 2: Stop (Space)")
    response = controller.stop()
    print(f"Response: {response}")
    time.sleep(0.5)
    
    # Test left
    print("\nTest 3: Left (A)")
    response = controller.left()
    print(f"Response: {response}")
    time.sleep(0.5)
    
    # Test right
    print("\nTest 4: Right (D)")
    response = controller.right()
    print(f"Response: {response}")
    time.sleep(0.5)
    
    # Test all off
    print("\nTest 5: All Off (X)")
    response = controller.all_off()
    print(f"Response: {response}")
    time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    
    controller.disconnect()

if __name__ == '__main__':
    test_arduino()

