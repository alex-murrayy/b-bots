"""
Arduino WASD Controller for Raspberry Pi
Controls the RC car Arduino via serial using W/S/A/D commands
Can be run remotely via SSH or as a service
"""

import serial
import time
import sys
import argparse
from typing import Optional


class ArduinoWASDController:
    """Controller for Arduino using WASD command protocol"""
    
    def __init__(self, port: str = '/dev/ttyACM0', baudrate: int = 115200, debug: bool = False):
        """
        Initialize Arduino Controller
        
        Args:
            port: Serial port (typically /dev/ttyACM0 or /dev/ttyUSB0 on Raspberry Pi)
            baudrate: Serial baud rate (default: 115200 to match Arduino sketch)
            debug: Enable debug output
        """
        self.port = port
        self.baudrate = baudrate
        self.serial: Optional[serial.Serial] = None
        self.is_connected = False
        self.debug = debug
        
    def connect(self, debug: bool = False):
        """Establish serial connection to Arduino"""
        try:
            if debug:
                print(f"[DEBUG] Attempting to connect to {self.port} at {self.baudrate} baud")
            
            self.serial = serial.Serial(
                self.port, 
                self.baudrate, 
                timeout=1,
                write_timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            if debug:
                print(f"[DEBUG] Serial port opened: {self.serial.is_open}")
                print(f"[DEBUG] Port settings: {self.serial}")
            
            # Wait for Arduino to initialize (Arduino resets on serial connection)
            # Some boards need time to initialize serial
            time.sleep(2.5)  # Increased wait time
            
            # Read startup messages from Arduino
            # Arduino sends: "WASD + Test Mode Ready" and help text
            startup_messages = []
            start_time = time.time()
            max_wait = 3.0  # Wait up to 3 seconds for startup messages
            
            if debug:
                print(f"[DEBUG] Reading startup messages (waiting up to {max_wait}s)...")
            
            while time.time() - start_time < max_wait:
                if self.serial.in_waiting > 0:
                    try:
                        # Read line by line
                        line = self.serial.readline()
                        if line:
                            text = line.decode('utf-8', errors='ignore').strip()
                            if text:
                                startup_messages.append(text)
                                if debug:
                                    print(f"[DEBUG] Startup: {text}")
                                # Stop if we got the main message
                                if 'WASD' in text or 'Ready' in text:
                                    # Still wait a bit more for help text
                                    time.sleep(0.5)
                                    break
                    except Exception as e:
                        if debug:
                            print(f"[DEBUG] Error reading startup: {e}")
                        break
                else:
                    time.sleep(0.1)
            
            # Read any remaining startup data
            if self.serial.in_waiting > 0:
                remaining = self.serial.read(self.serial.in_waiting)
                if debug and remaining:
                    try:
                        remaining_text = remaining.decode('utf-8', errors='ignore')
                        if remaining_text.strip():
                            if debug:
                                print(f"[DEBUG] Remaining startup: {remaining_text}")
                            startup_messages.append(remaining_text.strip())
                    except:
                        pass
            
            if debug:
                if startup_messages:
                    print(f"[DEBUG] Received {len(startup_messages)} startup message(s)")
                else:
                    print(f"[DEBUG] WARNING: No startup messages received!")
                    print(f"[DEBUG] This might indicate the sketch is not running")
            
            self.is_connected = True
            print(f"Connected to Arduino on {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Error connecting to {self.port}: {e}")
            print(f"Available ports: {self._list_ports()}")
            self.is_connected = False
            return False
        except Exception as e:
            print(f"Unexpected error connecting: {e}")
            if debug:
                import traceback
                traceback.print_exc()
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.is_connected and self.serial:
            self.serial.close()
            self.is_connected = False
            print("Disconnected from Arduino")
    
    def _list_ports(self):
        """List available serial ports"""
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def _send_command(self, command: str, debug: bool = False):
        """Send command to Arduino via serial"""
        if not self.is_connected or not self.serial:
            raise RuntimeError("Not connected to Arduino. Call connect() first.")
        
        # Ensure command is a single character (Arduino expects single char)
        original_command = command
        if len(command) > 1:
            # For multi-char commands like 'space', convert to single char
            if command.lower() == 'space' or command == ' ':
                command = ' '
            else:
                command = command[0]  # Take first character
        
        if debug:
            print(f"[DEBUG] Sending command: '{command}' (original: '{original_command}')")
            print(f"[DEBUG] Bytes waiting before send: {self.serial.in_waiting}")
        
        # Clear any pending input (but save for debug)
        pending_data = None
        if self.serial.in_waiting > 0:
            pending_data = self.serial.read(self.serial.in_waiting)
            if debug:
                try:
                    pending_str = pending_data.decode('utf-8', errors='ignore')
                    print(f"[DEBUG] Cleared pending data: {repr(pending_str)}")
                except:
                    print(f"[DEBUG] Cleared pending data (raw): {pending_data}")
        
        # Send command - Arduino sketch expects single character
        try:
            bytes_written = self.serial.write(command.encode('utf-8'))
            self.serial.flush()  # Ensure command is sent immediately
            if debug:
                print(f"[DEBUG] Wrote {bytes_written} byte(s): {repr(command.encode('utf-8'))}")
        except Exception as e:
            if debug:
                print(f"[DEBUG] Error writing command: {e}")
            raise RuntimeError(f"Failed to send command: {e}")
        
        # Wait for Arduino to process
        # Forward/Reverse have 100ms delay, steering has 200ms delay
        # Arduino also has Serial.println() which adds some delay
        time.sleep(0.3)  # Increased wait time for processing and response
        
        # Read Arduino response
        # Arduino sends responses like: "FWD", "REV", "LEFT TAP", "RIGHT TAP", etc.
        response = None
        response_lines = []
        max_wait_time = 1.5  # Wait up to 1.5 seconds for response
        start_time = time.time()
        bytes_read = 0
        
        if debug:
            print(f"[DEBUG] Waiting for response (timeout: {max_wait_time}s)...")
            print(f"[DEBUG] Bytes waiting: {self.serial.in_waiting}")
        
        # Try reading line by line (Arduino uses Serial.println)
        while time.time() - start_time < max_wait_time:
            if self.serial.in_waiting > 0:
                try:
                    # Read a line (Arduino sends lines with Serial.println)
                    line = self.serial.readline()
                    if line:
                        bytes_read += len(line)
                        try:
                            text = line.decode('utf-8', errors='ignore').strip()
                            if debug:
                                print(f"[DEBUG] Read line ({len(line)} bytes): {repr(text)}")
                            
                            if text and text not in ['', '\r', '\n']:
                                response_lines.append(text)
                                if debug:
                                    print(f"[DEBUG] Added response: {repr(text)}")
                                
                                # Arduino typically sends one response per command
                                # But wait a bit to see if more is coming
                                time.sleep(0.1)
                                if self.serial.in_waiting == 0:
                                    break
                        except UnicodeDecodeError as e:
                            if debug:
                                print(f"[DEBUG] Unicode decode error: {e}")
                                print(f"[DEBUG] Raw line: {repr(line)}")
                except Exception as e:
                    if debug:
                        print(f"[DEBUG] Error reading line: {e}")
                    break
            else:
                # No data yet, wait a bit
                time.sleep(0.05)
        
        # If we didn't get a line-based response, try reading raw data
        if not response_lines and self.serial.in_waiting > 0:
            if debug:
                print(f"[DEBUG] No line responses, trying raw read...")
            try:
                raw_data = self.serial.read(self.serial.in_waiting)
                bytes_read += len(raw_data)
                if debug:
                    print(f"[DEBUG] Raw data: {repr(raw_data)}")
                text = raw_data.decode('utf-8', errors='ignore').strip()
                if text:
                    response_lines.append(text)
            except Exception as e:
                if debug:
                    print(f"[DEBUG] Error reading raw data: {e}")
        
        # Return the first meaningful response
        for line in response_lines:
            if line and line.strip():
                response = line.strip()
                break
        
        if debug:
            if response:
                print(f"[DEBUG] Final response: {repr(response)}")
            else:
                print(f"[DEBUG] No response received (read {bytes_read} bytes total)")
                if bytes_read > 0:
                    print(f"[DEBUG] Response lines found: {response_lines}")
        
        return response
    
    def forward(self, debug: bool = None):
        """Move forward (W command)"""
        if debug is None:
            debug = self.debug
        return self._send_command('w', debug=debug)
    
    def backward(self, debug: bool = None):
        """Move backward (S command)"""
        if debug is None:
            debug = self.debug
        return self._send_command('s', debug=debug)
    
    def left(self, debug: bool = None):
        """Steer left tap (A command)"""
        if debug is None:
            debug = self.debug
        return self._send_command('a', debug=debug)
    
    def right(self, debug: bool = None):
        """Steer right tap (D command)"""
        if debug is None:
            debug = self.debug
        return self._send_command('d', debug=debug)
    
    def stop(self, debug: bool = None):
        """Stop drive (space command)"""
        if debug is None:
            debug = self.debug
        return self._send_command(' ', debug=debug)
    
    def center(self, debug: bool = None):
        """Center steering (C command)"""
        if debug is None:
            debug = self.debug
        return self._send_command('c', debug=debug)
    
    def all_off(self, debug: bool = None):
        """Turn everything off (X command)"""
        if debug is None:
            debug = self.debug
        return self._send_command('x', debug=debug)
    
    def test_mode(self, debug: bool = None):
        """Enter test mode (T command)"""
        if debug is None:
            debug = self.debug
        return self._send_command('t', debug=debug)
    
    def execute_command(self, cmd: str, debug: bool = False) -> Optional[str]:
        """
        Execute a command string
        
        Args:
            cmd: Command string (w, s, a, d, space, c, x, etc.)
            debug: Enable debug output
        
        Returns:
            Arduino response or None
        """
        cmd = cmd.lower().strip()
        
        command_map = {
            'w': self.forward,
            's': self.backward,
            'a': self.left,
            'd': self.right,
            ' ': self.stop,
            'space': self.stop,
            'stop': self.stop,
            'c': self.center,
            'center': self.center,
            'x': self.all_off,
            'off': self.all_off,
            't': self.test_mode,
            'test': self.test_mode,
        }
        
        if cmd in command_map:
            return command_map[cmd](debug=debug)
        else:
            return f"Unknown command: {cmd}"
    
    def set_debug(self, debug: bool):
        """Enable/disable debug mode"""
        self.debug = debug
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Arduino WASD Controller for RC Car')
    parser.add_argument('--port', '-p', default='/dev/ttyACM0', 
                       help='Serial port (default: /dev/ttyACM0)')
    parser.add_argument('--baudrate', '-b', type=int, default=115200,
                       help='Serial baud rate (default: 115200)')
    parser.add_argument('command', nargs='?', 
                       help='Command to execute: w(forward), s(backward), a(left), d(right), space(stop), c(center), x(off)')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('--list-ports', action='store_true',
                       help='List available serial ports')
    parser.add_argument('--debug', '-d', action='store_true',
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    # List ports if requested
    if args.list_ports:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        print("Available serial ports:")
        for port in ports:
            print(f"  {port.device} - {port.description}")
        return
    
    # Create controller
    controller = ArduinoWASDController(port=args.port, baudrate=args.baudrate, debug=args.debug)
    
    try:
        if not controller.connect(debug=args.debug):
            sys.exit(1)
        
        # Interactive mode
        if args.interactive:
            print("Interactive mode. Commands: w/s/a/d/space/c/x/q(quit)")
            print("Type 'help' for command list")
            while True:
                try:
                    cmd = input("> ").strip().lower()
                    if cmd == 'q' or cmd == 'quit':
                        break
                    elif cmd == 'help':
                        print("Commands:")
                        print("  w - Forward")
                        print("  s - Backward")
                        print("  a - Steer left")
                        print("  d - Steer right")
                        print("  space/stop - Stop drive")
                        print("  c/center - Center steering")
                        print("  x/off - All off")
                        print("  q/quit - Exit")
                        continue
                    
                    response = controller.execute_command(cmd, debug=args.debug)
                    if response:
                        print(f"Arduino: {response}")
                    else:
                        print("Command sent (no response)")
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    if args.debug:
                        import traceback
                        traceback.print_exc()
        
        # Single command mode
        elif args.command:
            response = controller.execute_command(args.command, debug=args.debug)
            if response:
                print(response)
            else:
                # Exit with success even if no response (command may have executed)
                sys.exit(0)
        else:
            parser.print_help()
    
    finally:
        controller.disconnect()


if __name__ == '__main__':
    main()

