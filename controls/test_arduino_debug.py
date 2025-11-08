#!/usr/bin/env python3
"""
Comprehensive Arduino test script with detailed debugging
Tests connection, communication, and command execution
"""

import sys
import time
import argparse

try:
    from arduino_wasd_controller import ArduinoWASDController
except ImportError:
    print("Error: Could not import arduino_wasd_controller")
    print("Make sure you're running from the project root or controls directory")
    sys.exit(1)


def test_connection(port: str, debug: bool = False):
    """Test basic connection to Arduino"""
    print(f"\n{'='*70}")
    print("TEST 1: Connection Test")
    print(f"{'='*70}")
    
    controller = ArduinoWASDController(port=port, debug=debug)
    
    print(f"Attempting to connect to {port}...")
    if not controller.connect(debug=debug):
        print("FAILED: Could not connect to Arduino")
        return None
    
    print("SUCCESS: Connected to Arduino")
    
    # Wait a moment and check for startup messages
    print("\nChecking for Arduino startup messages...")
    time.sleep(0.5)
    if controller.serial and controller.serial.in_waiting > 0:
        startup = controller.serial.read(controller.serial.in_waiting)
        try:
            startup_msg = startup.decode('utf-8', errors='ignore')
            print(f"Startup message: {startup_msg}")
        except:
            print(f"Startup data (raw): {startup}")
    else:
        print("No startup messages detected")
    
    return controller


def test_serial_communication(controller: ArduinoWASDController, debug: bool = False):
    """Test serial communication"""
    print(f"\n{'='*70}")
    print("TEST 2: Serial Communication Test")
    print(f"{'='*70}")
    
    if not controller.is_connected:
        print("ERROR: Not connected to Arduino")
        return False
    
    # Test sending a command and reading response
    print("\nSending test command 'w' (forward)...")
    response = controller.forward(debug=debug)
    
    print(f"Response received: {repr(response)}")
    if response:
        print(f"SUCCESS: Arduino responded with: {response}")
        return True
    else:
        print("WARNING: No response received from Arduino")
        print("This might be normal if Arduino doesn't send responses, or")
        print("there might be a communication issue.")
        return False


def test_all_commands(controller: ArduinoWASDController, debug: bool = False):
    """Test all commands"""
    print(f"\n{'='*70}")
    print("TEST 3: Command Execution Test")
    print(f"{'='*70}")
    
    tests = [
        ('w', 'Forward', controller.forward),
        (' ', 'Stop', controller.stop),
        ('s', 'Backward', controller.backward),
        (' ', 'Stop', controller.stop),
        ('a', 'Left', controller.left),
        ('d', 'Right', controller.right),
        ('c', 'Center', controller.center),
        ('x', 'All Off', controller.all_off),
    ]
    
    results = []
    
    for cmd, name, func in tests:
        print(f"\nTesting: {name} ('{cmd}')")
        try:
            start_time = time.time()
            response = func(debug=debug)
            elapsed = time.time() - start_time
            
            if response:
                print(f"  Response: {response} (took {elapsed:.3f}s)")
                results.append((name, True, response))
            else:
                print(f"  No response (took {elapsed:.3f}s)")
                results.append((name, False, None))
            
            time.sleep(0.3)  # Small delay between commands
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append((name, False, str(e)))
    
    return results


def test_response_timing(controller: ArduinoWASDController, debug: bool = False):
    """Test response timing"""
    print(f"\n{'='*70}")
    print("TEST 4: Response Timing Test")
    print(f"{'='*70}")
    
    print("\nSending multiple 'w' commands and measuring response times...")
    
    times = []
    responses = []
    
    for i in range(5):
        print(f"  Test {i+1}/5...", end=' ', flush=True)
        start = time.time()
        response = controller.forward(debug=False)  # Don't debug each one
        elapsed = time.time() - start
        times.append(elapsed)
        responses.append(response)
        print(f"Response: {repr(response)}, Time: {elapsed:.3f}s")
        time.sleep(0.2)
    
    controller.stop()
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        print(f"\nTiming Statistics:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Min: {min_time:.3f}s")
        print(f"  Max: {max_time:.3f}s")
    
    return times, responses


def test_raw_serial(controller: ArduinoWASDController):
    """Test raw serial communication"""
    print(f"\n{'='*70}")
    print("TEST 5: Raw Serial Communication Test")
    print(f"{'='*70}")
    
    if not controller.serial:
        print("ERROR: Serial connection not available")
        return
    
    print("\nTesting raw serial write/read...")
    
    # Send raw 'w' command
    print("Sending raw 'w' byte...")
    controller.serial.write(b'w')
    controller.serial.flush()
    
    # Wait and read
    time.sleep(0.3)
    if controller.serial.in_waiting > 0:
        raw_response = controller.serial.read(controller.serial.in_waiting)
        print(f"Raw response: {repr(raw_response)}")
        try:
            text_response = raw_response.decode('utf-8', errors='ignore')
            print(f"Decoded response: {repr(text_response)}")
        except:
            print("Could not decode response")
    else:
        print("No response received")


def main():
    parser = argparse.ArgumentParser(description='Comprehensive Arduino Test with Debugging')
    parser.add_argument('--port', '-p', default='/dev/ttyACM0',
                       help='Serial port (default: /dev/ttyACM0)')
    parser.add_argument('--debug', '-d', action='store_true',
                       help='Enable debug output')
    parser.add_argument('--test', choices=['all', 'connection', 'communication', 'commands', 'timing', 'raw'],
                       default='all',
                       help='Which test to run (default: all)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("ARDUINO COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"Port: {args.port}")
    print(f"Debug: {args.debug}")
    print(f"Test: {args.test}")
    
    controller = None
    
    try:
        # Test 1: Connection
        if args.test in ['all', 'connection']:
            controller = test_connection(args.port, debug=args.debug)
            if not controller:
                print("\nCannot continue without connection. Exiting.")
                sys.exit(1)
        
        if not controller:
            controller = ArduinoWASDController(port=args.port, debug=args.debug)
            if not controller.connect(debug=args.debug):
                print("Failed to connect")
                sys.exit(1)
        
        # Test 2: Serial Communication
        if args.test in ['all', 'communication']:
            test_serial_communication(controller, debug=args.debug)
        
        # Test 3: All Commands
        if args.test in ['all', 'commands']:
            results = test_all_commands(controller, debug=args.debug)
            print(f"\n{'='*70}")
            print("COMMAND TEST SUMMARY")
            print(f"{'='*70}")
            for name, success, response in results:
                status = "PASS" if success else "FAIL"
                resp_str = f" ({response})" if response else ""
                print(f"  {name:15} - {status}{resp_str}")
        
        # Test 4: Response Timing
        if args.test in ['all', 'timing']:
            test_response_timing(controller, debug=args.debug)
        
        # Test 5: Raw Serial
        if args.test in ['all', 'raw']:
            test_raw_serial(controller)
        
        print(f"\n{'='*70}")
        print("ALL TESTS COMPLETED")
        print(f"{'='*70}")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
    finally:
        if controller:
            controller.stop()
            controller.all_off()
            controller.disconnect()
            print("\nDisconnected from Arduino")


if __name__ == '__main__':
    main()

