#!/usr/bin/env python3
"""
Verify Arduino sketch is running correctly
Checks for startup messages and basic communication
"""

import serial
import time
import sys


def verify_sketch(port: str = '/dev/ttyACM0', baudrate: int = 115200):
    """Verify the Arduino sketch is running"""
    print("=" * 70)
    print("ARDUINO SKETCH VERIFICATION")
    print("=" * 70)
    print(f"Port: {port}")
    print(f"Baud rate: {baudrate}")
    print()
    
    try:
        # Connect to Arduino
        print("Connecting to Arduino...")
        ser = serial.Serial(port, baudrate, timeout=2)
        time.sleep(2.5)  # Wait for Arduino reset and initialization
        
        print("✓ Connected")
        print("\n" + "-" * 70)
        print("STEP 1: Check for startup messages")
        print("-" * 70)
        print("Expected: 'WASD + Test Mode Ready'")
        print("Reading for 3 seconds...\n")
        
        startup_found = False
        messages = []
        start_time = time.time()
        
        while time.time() - start_time < 3.0:
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
                except:
                    pass
            time.sleep(0.1)
        
        if startup_found:
            print("\n✓ Startup message found - Sketch is running!")
        elif messages:
            print(f"\n⚠️  Received {len(messages)} message(s) but not expected startup")
            print("   Sketch may be running but sending different messages")
        else:
            print("\n✗ No startup messages received")
            print("   Possible issues:")
            print("   - Sketch is not uploaded")
            print("   - Sketch is not running")
            print("   - Wrong baud rate")
            print("   - Serial.println() is not in setup()")
        
        print("\n" + "-" * 70)
        print("STEP 2: Test command 'w' (forward)")
        print("-" * 70)
        
        # Clear buffer
        time.sleep(0.1)
        if ser.in_waiting > 0:
            ser.read(ser.in_waiting)
        
        # Send 'w' command
        print("Sending 'w' command...")
        ser.write(b'w')
        ser.flush()
        
        # Wait for response
        print("Waiting for response (looking for 'FWD')...")
        time.sleep(0.5)
        
        response_found = False
        responses = []
        start_time = time.time()
        
        while time.time() - start_time < 1.5:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline()
                    if line:
                        text = line.decode('utf-8', errors='ignore').strip()
                        if text:
                            responses.append(text)
                            print(f"  → {text}")
                            if 'FWD' in text or 'Fwd' in text or 'Forward' in text:
                                response_found = True
                except:
                    pass
            time.sleep(0.05)
        
        if response_found:
            print("\n✓ Command response received - Communication working!")
        elif responses:
            print(f"\n⚠️  Received {len(responses)} response(s) but not expected format")
        else:
            print("\n✗ No response received")
            print("   Possible issues:")
            print("   - Sketch is not processing commands")
            print("   - Serial.println() is not in command handlers")
            print("   - Response timing is off")
        
        print("\n" + "-" * 70)
        print("STEP 3: Test all commands")
        print("-" * 70)
        
        commands = [
            ('w', 'Forward', 'FWD'),
            (' ', 'Stop', 'NEUTRAL'),
            ('s', 'Backward', 'REV'),
            ('a', 'Left', 'LEFT'),
            ('d', 'Right', 'RIGHT'),
            ('c', 'Center', 'CENTER'),
            ('x', 'All Off', 'ALL OFF'),
        ]
        
        results = []
        for cmd, name, expected in commands:
            time.sleep(0.2)
            if ser.in_waiting > 0:
                ser.read(ser.in_waiting)  # Clear buffer
            
            print(f"Testing '{cmd}' ({name})...", end=' ', flush=True)
            ser.write(cmd.encode())
            ser.flush()
            
            time.sleep(0.3)
            response = None
            if ser.in_waiting > 0:
                try:
                    line = ser.readline()
                    if line:
                        response = line.decode('utf-8', errors='ignore').strip()
                except:
                    pass
            
            if response:
                print(f"✓ {response}")
                results.append((name, True, response))
            else:
                print("✗ No response")
                results.append((name, False, None))
        
        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)
        print(f"Startup message: {'✓' if startup_found else '✗'}")
        print(f"Command responses: {sum(1 for _, success, _ in results if success)}/{len(results)}")
        print()
        print("Command test results:")
        for name, success, response in results:
            status = '✓' if success else '✗'
            resp_str = f" ({response})" if response else ""
            print(f"  {status} {name:10} {resp_str}")
        
        if not startup_found and not any(success for _, success, _ in results):
            print("\n" + "!" * 70)
            print("CRITICAL: Arduino sketch may not be running correctly!")
            print("!" * 70)
            print("\nActions to take:")
            print("1. Open Arduino IDE")
            print("2. Verify sketch 'arduinoControls.ino' is uploaded")
            print("3. Open Serial Monitor (Tools -> Serial Monitor)")
            print("4. Set baud rate to 115200")
            print("5. Check if you see 'WASD + Test Mode Ready' message")
            print("6. Try sending 'w' manually and see if you get 'FWD' response")
            print("7. If nothing appears, re-upload the sketch")
        
        ser.close()
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Verify Arduino sketch is running')
    parser.add_argument('--port', '-p', default='/dev/ttyACM0',
                       help='Serial port')
    parser.add_argument('--baudrate', '-b', type=int, default=115200,
                       help='Baud rate (default: 115200)')
    args = parser.parse_args()
    verify_sketch(args.port, args.baudrate)

