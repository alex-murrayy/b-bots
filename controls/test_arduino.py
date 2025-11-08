#!/usr/bin/env python3
"""
Simple test script to verify Arduino connection and commands
With comprehensive debugging and error handling
"""

import sys
import time
import argparse

try:
    from arduino_wasd_controller import ArduinoWASDController
except ImportError:
    print("Error: Could not import arduino_wasd_controller")
    print("Make sure you're running from the controls directory or project root")
    sys.exit(1)


def test_arduino(port: str = '/dev/ttyACM0', debug: bool = False):
    """Test Arduino connection and basic commands"""
    print(f"Testing Arduino connection on {port}...")
    print("=" * 60)
    
    try:
        controller = ArduinoWASDController(port=port, debug=debug)
        
        if not controller.connect(debug=debug):
            print("FAILED: Could not connect to Arduino")
            print("\nTroubleshooting:")
            print("1. Check Arduino is connected via USB")
            print("2. Check port: python3 controls/arduino_wasd_controller.py --list-ports")
            print("3. Check permissions: sudo usermod -a -G dialout $USER")
            print("4. Try different port: python3 controls/test_arduino.py --port /dev/ttyUSB0")
            sys.exit(1)
        
        print("SUCCESS: Connected to Arduino")
        
        # Wait a moment for any startup messages
        time.sleep(0.5)
        if controller.serial and controller.serial.in_waiting > 0:
            startup = controller.serial.read(controller.serial.in_waiting)
            try:
                startup_msg = startup.decode('utf-8', errors='ignore').strip()
                if startup_msg:
                    print(f"Arduino startup message: {startup_msg}")
            except:
                pass
        
        print("\nTesting commands...")
        print("=" * 60)
        
        # Test forward
        print("\nTest 1: Forward (W)")
        try:
            response = controller.forward(debug=debug)
            if response:
                print(f"  Response: {response}")
            else:
                print(f"  Response: None (command sent, no response received)")
                print(f"  NOTE: This is OK if Arduino executes command but doesn't send response")
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(1)
        
        # Test stop
        print("\nTest 2: Stop (Space)")
        try:
            response = controller.stop(debug=debug)
            if response:
                print(f"  Response: {response}")
            else:
                print(f"  Response: None")
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(0.5)
        
        # Test left
        print("\nTest 3: Left (A)")
        try:
            response = controller.left(debug=debug)
            if response:
                print(f"  Response: {response}")
            else:
                print(f"  Response: None")
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(0.5)
        
        # Test right
        print("\nTest 4: Right (D)")
        try:
            response = controller.right(debug=debug)
            if response:
                print(f"  Response: {response}")
            else:
                print(f"  Response: None")
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(0.5)
        
        # Test all off
        print("\nTest 5: All Off (X)")
        try:
            response = controller.all_off(debug=debug)
            if response:
                print(f"  Response: {response}")
            else:
                print(f"  Response: None")
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(0.5)
        
        # Check for any remaining data
        print("\nChecking for any remaining Arduino output...")
        time.sleep(0.2)
        if controller.serial and controller.serial.in_waiting > 0:
            remaining = controller.serial.read(controller.serial.in_waiting)
            try:
                remaining_str = remaining.decode('utf-8', errors='ignore').strip()
                if remaining_str:
                    print(f"  Remaining data: {remaining_str}")
            except:
                print(f"  Remaining data (raw): {remaining}")
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("\nNOTE: If responses are None but Arduino LED is flashing,")
        print("      the Arduino is receiving commands correctly.")
        print("      Responses may not be necessary if commands execute properly.")
        
        controller.disconnect()
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        if controller:
            controller.all_off()
            controller.disconnect()
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        if controller:
            controller.all_off()
            controller.disconnect()
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test Arduino connection and commands')
    parser.add_argument('--port', '-p', default='/dev/ttyACM0',
                       help='Serial port (default: /dev/ttyACM0)')
    parser.add_argument('--debug', '-d', action='store_true',
                       help='Enable debug output')
    
    args = parser.parse_args()
    test_arduino(port=args.port, debug=args.debug)
