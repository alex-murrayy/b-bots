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
    
    def __init__(self, port: str = '/dev/ttyACM0', baudrate: int = 9600):
        """
        Initialize Arduino Controller
        
        Args:
            port: Serial port (typically /dev/ttyACM0 or /dev/ttyUSB0 on Raspberry Pi)
            baudrate: Serial baud rate (default: 9600 to match Arduino sketch)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial: Optional[serial.Serial] = None
        self.is_connected = False
        
    def connect(self):
        """Establish serial connection to Arduino"""
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino to initialize
            self.is_connected = True
            print(f"Connected to Arduino on {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Error connecting to {self.port}: {e}")
            print(f"Available ports: {self._list_ports()}")
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
    
    def _send_command(self, command: str):
        """Send command to Arduino via serial"""
        if not self.is_connected or not self.serial:
            raise RuntimeError("Not connected to Arduino. Call connect() first.")
        
        self.serial.write(command.encode())
        time.sleep(0.05)  # Small delay for command processing
        
        # Read Arduino response if available
        if self.serial.in_waiting > 0:
            response = self.serial.readline().decode().strip()
            if response:
                return response
        return None
    
    def forward(self):
        """Move forward (W command)"""
        return self._send_command('W')
    
    def backward(self):
        """Move backward (S command)"""
        return self._send_command('S')
    
    def left(self):
        """Steer left tap (A command)"""
        return self._send_command('A')
    
    def right(self):
        """Steer right tap (D command)"""
        return self._send_command('D')
    
    def stop(self):
        """Stop drive (space command)"""
        return self._send_command(' ')
    
    def center(self):
        """Center steering (C command)"""
        return self._send_command('C')
    
    def all_off(self):
        """Turn everything off (X command)"""
        return self._send_command('X')
    
    def test_mode(self):
        """Enter test mode (T command)"""
        return self._send_command('T')
    
    def execute_command(self, cmd: str) -> Optional[str]:
        """
        Execute a command string
        
        Args:
            cmd: Command string (w, s, a, d, space, c, x, etc.)
        
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
            return command_map[cmd]()
        else:
            return f"Unknown command: {cmd}"
    
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
    parser.add_argument('--baudrate', '-b', type=int, default=9600,
                       help='Serial baud rate (default: 9600)')
    parser.add_argument('command', nargs='?', 
                       help='Command to execute: w(forward), s(backward), a(left), d(right), space(stop), c(center), x(off)')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('--list-ports', action='store_true',
                       help='List available serial ports')
    
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
    controller = ArduinoWASDController(port=args.port, baudrate=args.baudrate)
    
    try:
        if not controller.connect():
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
                    
                    response = controller.execute_command(cmd)
                    if response:
                        print(f"Arduino: {response}")
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Error: {e}")
        
        # Single command mode
        elif args.command:
            response = controller.execute_command(args.command)
            if response:
                print(response)
        else:
            parser.print_help()
    
    finally:
        controller.disconnect()


if __name__ == '__main__':
    main()

