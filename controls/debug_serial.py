#!/usr/bin/env python3
"""
Serial communication debug tool
Monitors serial communication in real-time
"""

import serial
import time
import sys
import argparse
import threading


def monitor_serial(port: str, baudrate: int = 9600):
    """Monitor serial communication"""
    print(f"Monitoring serial port {port} at {baudrate} baud...")
    print("Press Ctrl+C to stop\n")
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
        
        print("=" * 60)
        print("SERIAL MONITOR - Reading all data from Arduino")
        print("=" * 60)
        print("Waiting for data...\n")
        
        # Clear startup messages
        time.sleep(0.5)
        if ser.in_waiting > 0:
            startup = ser.read(ser.in_waiting)
            try:
                print(f"Startup: {startup.decode('utf-8', errors='ignore')}")
            except:
                print(f"Startup (raw): {startup}")
        
        print("\n" + "-" * 60)
        print("Now monitoring... Send commands from another terminal")
        print("Or type commands here (w/s/a/d/space/c/x):")
        print("-" * 60 + "\n")
        
        running = True
        
        def read_loop():
            """Read data from Arduino"""
            while running:
                if ser.in_waiting > 0:
                    try:
                        data = ser.read(ser.in_waiting)
                        text = data.decode('utf-8', errors='ignore')
                        if text.strip():
                            print(f"[ARDUINO] {text.strip()}")
                    except Exception as e:
                        print(f"[ERROR] {e}")
                time.sleep(0.01)
        
        # Start reading thread
        read_thread = threading.Thread(target=read_loop, daemon=True)
        read_thread.start()
        
        # Main loop - send commands
        try:
            while True:
                try:
                    cmd = input().strip()
                    if not cmd:
                        continue
                    
                    if cmd in ['q', 'quit', 'exit']:
                        break
                    
                    # Send command
                    ser.write(cmd.encode('utf-8'))
                    ser.flush()
                    print(f"[SENT] '{cmd}'")
                    time.sleep(0.1)
                    
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
        except KeyboardInterrupt:
            pass
        finally:
            running = False
            ser.close()
            print("\nClosed serial port")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Serial Communication Debug Tool')
    parser.add_argument('--port', '-p', default='/dev/ttyACM0',
                       help='Serial port (default: /dev/ttyACM0)')
    parser.add_argument('--baudrate', '-b', type=int, default=9600,
                       help='Baud rate (default: 9600)')
    
    args = parser.parse_args()
    monitor_serial(args.port, args.baudrate)


if __name__ == '__main__':
    main()

