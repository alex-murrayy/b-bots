#!/usr/bin/env python3
"""
Check Arduino connection and verify sketch is running
Reads startup messages and continuously monitors serial
"""

import serial
import time
import sys
import argparse


def check_arduino(port: str = '/dev/ttyACM0', baudrate: int = 9600):
    """Check if Arduino is responding"""
    print(f"Checking Arduino on {port} at {baudrate} baud...")
    print("=" * 70)
    
    try:
        # Open serial connection
        print(f"\n1. Opening serial port...")
        ser = serial.Serial(port, baudrate, timeout=2)
        print(f"   ✓ Serial port opened")
        
        # Wait for Arduino to reset (Arduino resets on serial connection)
        print(f"\n2. Waiting for Arduino to initialize (2 seconds)...")
        time.sleep(2)
        
        # Read startup messages
        print(f"\n3. Reading Arduino startup messages...")
        startup_messages = []
        start_time = time.time()
        
        while time.time() - start_time < 3.0:  # Read for up to 3 seconds
            if ser.in_waiting > 0:
                try:
                    line = ser.readline()
                    if line:
                        text = line.decode('utf-8', errors='ignore').strip()
                        if text:
                            startup_messages.append(text)
                            print(f"   → {text}")
                except:
                    pass
            else:
                time.sleep(0.1)
        
        if not startup_messages:
            print("   ⚠️  No startup messages received")
            print("   This might mean:")
            print("     - Arduino sketch is not running")
            print("     - Sketch doesn't send Serial.println() on startup")
            print("     - Wrong baud rate")
        else:
            print(f"   ✓ Received {len(startup_messages)} startup message(s)")
        
        # Test: Send a command and see if we get response
        print(f"\n4. Testing command communication...")
        print(f"   Sending 'w' command...")
        
        # Clear any remaining data
        time.sleep(0.1)
        if ser.in_waiting > 0:
            ser.read(ser.in_waiting)
        
        # Send command
        ser.write(b'w')
        ser.flush()
        print(f"   ✓ Command sent")
        
        # Wait and read response
        print(f"   Waiting for response (2 seconds)...")
        time.sleep(0.3)  # Wait for Arduino to process
        
        responses = []
        start_time = time.time()
        while time.time() - start_time < 2.0:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline()
                    if line:
                        text = line.decode('utf-8', errors='ignore').strip()
                        if text:
                            responses.append(text)
                            print(f"   → Response: {text}")
                except Exception as e:
                    print(f"   Error reading: {e}")
            else:
                time.sleep(0.05)
        
        if responses:
            print(f"   ✓ Received {len(responses)} response(s)")
        else:
            print(f"   ⚠️  No response received")
            print(f"   This could mean:")
            print(f"     - Arduino is receiving but not responding")
            print(f"     - Sketch doesn't have Serial.println() for this command")
            print(f"     - Response timing is off")
        
        # Continuous monitoring test
        print(f"\n5. Continuous monitoring test (10 seconds)...")
        print(f"   Send commands from Arduino Serial Monitor or another terminal")
        print(f"   Press Ctrl+C to stop early\n")
        
        try:
            start_time = time.time()
            last_activity = time.time()
            
            while time.time() - start_time < 10.0:
                if ser.in_waiting > 0:
                    try:
                        # Read all available data
                        data = ser.read(ser.in_waiting)
                        text = data.decode('utf-8', errors='ignore')
                        if text.strip():
                            print(f"   [{time.time() - start_time:.1f}s] Arduino: {text.strip()}")
                            last_activity = time.time()
                    except Exception as e:
                        print(f"   Error: {e}")
                
                # Send a test command every 2 seconds
                if time.time() - last_activity > 2.0:
                    ser.write(b't')  # Test mode command
                    ser.flush()
                    last_activity = time.time()
                    print(f"   [{time.time() - start_time:.1f}s] Sent 't' (test mode)")
                    time.sleep(0.1)
                
                time.sleep(0.05)
        except KeyboardInterrupt:
            print("\n   Stopped by user")
        
        # Summary
        print(f"\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Connection: {'✓ OK' if ser.is_open else '✗ FAILED'}")
        print(f"Startup messages: {len(startup_messages)}")
        print(f"Command responses: {len(responses)}")
        
        if len(startup_messages) == 0 and len(responses) == 0:
            print(f"\n⚠️  WARNING: No communication detected from Arduino")
            print(f"   Possible issues:")
            print(f"   1. Arduino sketch is not uploaded or not running")
            print(f"   2. Wrong baud rate (try 115200 or check Arduino sketch)")
            print(f"   3. Arduino is in wrong mode")
            print(f"   4. Serial connection issue")
            print(f"\n   Recommendations:")
            print(f"   - Open Arduino IDE Serial Monitor (9600 baud)")
            print(f"   - Verify sketch is uploaded")
            print(f"   - Check if Arduino LED blinks on upload")
            print(f"   - Try different baud rate: python3 check_arduino.py --baudrate 115200")
        
        ser.close()
        
    except serial.SerialException as e:
        print(f"✗ ERROR: {e}")
        print(f"\nTroubleshooting:")
        print(f"1. Check Arduino is connected: ls -l /dev/ttyACM*")
        print(f"2. Check permissions: groups (should include 'dialout')")
        print(f"3. Try different port: python3 check_arduino.py --port /dev/ttyUSB0")
        sys.exit(1)
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Check Arduino connection and communication')
    parser.add_argument('--port', '-p', default='/dev/ttyACM0',
                       help='Serial port (default: /dev/ttyACM0)')
    parser.add_argument('--baudrate', '-b', type=int, default=9600,
                       help='Baud rate (default: 9600)')
    
    args = parser.parse_args()
    check_arduino(args.port, args.baudrate)


if __name__ == '__main__':
    main()

