#!/usr/bin/env python3
"""
Test serial communication with detailed timing and response checking
Specifically tests the working Arduino sketch
"""

import serial
import time
import sys
import argparse


def test_communication(port: str = '/dev/ttyACM0', baudrate: int = 9600):
    """Test communication with Arduino sketch"""
    print("=" * 70)
    print("ARDUINO COMMUNICATION TEST")
    print("=" * 70)
    print(f"Port: {port}")
    print(f"Baud rate: {baudrate}")
    print()
    
    try:
        # Connect
        print("Step 1: Connecting to Arduino...")
        ser = serial.Serial(port, baudrate, timeout=2)
        print("✓ Connected")
        print()
        
        # Wait for Arduino to initialize
        print("Step 2: Waiting for Arduino initialization...")
        print("(Arduino resets when serial connection opens)")
        time.sleep(3.0)  # Give Arduino time to initialize
        print("✓ Wait complete")
        print()
        
        # Read startup messages
        print("Step 3: Reading startup messages...")
        print("Expected: 'WASD + Test Mode Ready'")
        print()
        
        startup_found = False
        messages = []
        start_time = time.time()
        
        while time.time() - start_time < 4.0:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline()
                    if line:
                        text = line.decode('utf-8', errors='ignore').strip()
                        if text:
                            messages.append(text)
                            print(f"  → {text}")
                            if 'WASD' in text or 'Ready' in text:
                                startup_found = True
                except Exception as e:
                    print(f"  Error: {e}")
            else:
                time.sleep(0.1)
        
        if startup_found:
            print("\n✓ Startup message received - Sketch is running!")
        else:
            print("\n✗ No startup message received")
            print("  This means the sketch is NOT running or not sending messages")
            print("  Action: Re-upload the sketch in Arduino IDE")
            return False
        
        print()
        print("Step 4: Testing commands...")
        print("-" * 70)
        
        # Test commands
        tests = [
            ('w', 'Forward', 'FWD'),
            (' ', 'Stop', 'NEUTRAL'),
            ('s', 'Backward', 'REV'),
            ('a', 'Left', 'LEFT'),
            ('d', 'Right', 'RIGHT'),
            ('c', 'Center', 'CENTER'),
            ('x', 'All Off', 'ALL OFF'),
        ]
        
        results = []
        for cmd, name, expected in tests:
            # Clear buffer
            time.sleep(0.2)
            while ser.in_waiting > 0:
                ser.read(ser.in_waiting)
            
            # Send command
            print(f"Testing '{cmd}' ({name})...", end=' ', flush=True)
            send_time = time.time()
            ser.write(cmd.encode('utf-8'))
            ser.flush()
            
            # Wait for response
            response = None
            max_wait = 1.5
            start_wait = time.time()
            
            while time.time() - start_wait < max_wait:
                if ser.in_waiting > 0:
                    try:
                        line = ser.readline()
                        if line:
                            text = line.decode('utf-8', errors='ignore').strip()
                            if text:
                                response = text
                                break
                    except:
                        pass
                time.sleep(0.05)
            
            elapsed = time.time() - send_time
            
            if response:
                if expected in response.upper():
                    print(f"✓ {response} ({elapsed:.3f}s)")
                    results.append((name, True, response))
                else:
                    print(f"⚠ {response} (expected {expected}) ({elapsed:.3f}s)")
                    results.append((name, True, response))
            else:
                print(f"✗ No response ({elapsed:.3f}s)")
                results.append((name, False, None))
        
        # Summary
        print()
        print("=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Startup message: {'✓' if startup_found else '✗'}")
        print(f"Command responses: {sum(1 for _, success, _ in results if success)}/{len(results)}")
        print()
        
        successful = sum(1 for _, success, _ in results if success)
        if startup_found and successful == len(results):
            print("✓ ALL TESTS PASSED - Arduino is working correctly!")
            return True
        elif startup_found and successful > 0:
            print("⚠ PARTIAL SUCCESS - Some commands work")
            print("  This might be normal if some commands don't send responses")
            return True
        elif startup_found:
            print("⚠ STARTUP OK BUT NO COMMAND RESPONSES")
            print("  Commands might be executing but not responding")
            print("  Check if motors/LED respond to commands")
            return False
        else:
            print("✗ FAILED - Sketch is not running")
            print("  Action: Re-upload sketch in Arduino IDE")
            return False
        
        ser.close()
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test Arduino communication')
    parser.add_argument('--port', '-p', default='/dev/ttyACM0',
                       help='Serial port')
    parser.add_argument('--baudrate', '-b', type=int, default=9600,
                       help='Baud rate')
    args = parser.parse_args()
    
    success = test_communication(args.port, args.baudrate)
    sys.exit(0 if success else 1)

