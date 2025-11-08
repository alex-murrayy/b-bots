#!/usr/bin/env python3
"""
Simple Interactive RC Car Control
Easier version that works without special terminal setup
Just type commands and press Enter
Works both locally on Pi and remotely via SSH
"""

import sys
import subprocess
import argparse
import threading
import time
import os
import socket
from pathlib import Path

# Try to import the Arduino controller for direct connection
try:
    from arduino_wasd_controller import ArduinoWASDController
    HAS_CONTROLLER = True
except ImportError:
    HAS_CONTROLLER = False


class SimpleInteractiveControl:
    """Simple interactive controller - type commands and press Enter"""
    
    def __init__(self, pi_host: str = None, pi_user: str = 'pi',
                 script_path: str = None,
                 use_service: bool = False, service_file: str = '/tmp/rc_car_command',
                 arduino_port: str = '/dev/ttyACM0', arduino_baudrate: int = 115200, local_mode: bool = None):
        """
        Initialize controller
        
        Args:
            pi_host: Raspberry Pi hostname (None = auto-detect local)
            pi_user: SSH username
            script_path: Path to controller script
            use_service: Use file-based service
            service_file: Command file path
            arduino_port: Arduino port for local mode
            local_mode: Force local mode (None = auto-detect)
        """
        self.pi_host = pi_host
        self.pi_user = pi_user
        # Auto-detect script path if not provided
        if script_path is None:
            # Try to find the controller in the same directory or common locations
            script_dir = os.path.dirname(os.path.abspath(__file__))
            local_script = os.path.join(script_dir, 'arduino_wasd_controller.py')
            if os.path.exists(local_script):
                script_path = local_script
            else:
                script_path = '~/rc_car_control/arduino_wasd_controller.py'
        self.script_path = script_path
        self.use_service = use_service
        self.service_file = service_file
        self.arduino_port = arduino_port
        self.running = True
        self.local_controller = None
        
        # Auto-detect if running locally
        if local_mode is None:
            self.is_local = self._detect_local_mode()
        else:
            self.is_local = local_mode
        
        # If running locally and controller available, use direct connection
        if self.is_local and HAS_CONTROLLER and not use_service:
            try:
                self.local_controller = ArduinoWASDController(port=arduino_port, baudrate=arduino_baudrate)
                if self.local_controller.connect():
                    print(f"Connected directly to Arduino on {arduino_port} at {arduino_baudrate} baud")
                else:
                    self.local_controller = None
            except Exception as e:
                print(f"Could not connect directly: {e}")
                self.local_controller = None
    
    def _detect_local_mode(self) -> bool:
        """Detect if we're running on the Pi locally"""
        # Check if pi_host is None or localhost
        if self.pi_host is None:
            return True
        
        # Check if pi_host resolves to localhost
        try:
            hostname = socket.gethostname()
            if self.pi_host in [hostname, 'localhost', '127.0.0.1', 'raspberrypi', 'raspberrypi.local']:
                # Double check by resolving
                if socket.gethostbyname(self.pi_host) in ['127.0.0.1', '::1']:
                    return True
                # Or check if hostname matches
                if self.pi_host.startswith(hostname.split('.')[0]):
                    return True
        except:
            pass
        
        return False
    
    def _send_command_local(self, command: str):
        """Send command via direct Arduino connection"""
        if self.local_controller:
            try:
                self.local_controller.execute_command(command)
            except Exception as e:
                print(f"Error sending command: {e}")
        else:
            # Fallback to running script locally
            script_path = os.path.expanduser(self.script_path)
            if os.path.exists(script_path):
                subprocess.run(
                    ['python3', script_path, command],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=2
                )
    
    def _send_command_service_file(self, command: str):
        """Send command via service file (local)"""
        try:
            with open(self.service_file, 'w') as f:
                f.write(command)
        except Exception as e:
            print(f"Error writing to service file: {e}")
    
    def _send_command_ssh(self, command: str):
        """Send command via SSH"""
        ssh_cmd = f'ssh {self.pi_user}@{self.pi_host} "python3 {self.script_path} {command}"'
        try:
            subprocess.run(ssh_cmd, shell=True, stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL, timeout=2)
        except subprocess.TimeoutExpired:
            pass  # Ignore timeouts
    
    def _send_command_service(self, command: str):
        """Send command via service file (remote)"""
        ssh_cmd = f'ssh {self.pi_user}@{self.pi_host} "echo \\"{command}\\" > {self.service_file}"'
        try:
            subprocess.run(ssh_cmd, shell=True, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL, timeout=1)
        except subprocess.TimeoutExpired:
            pass  # Ignore timeouts
    
    def send_command(self, command: str):
        """Send command to RC car"""
        if self.is_local:
            # Running locally on Pi
            if self.use_service:
                self._send_command_service_file(command)
            else:
                self._send_command_local(command)
        else:
            # Running remotely, use SSH
            if self.use_service:
                self._send_command_service(command)
            else:
                self._send_command_ssh(command)
    
    def print_help(self):
        """Print help message"""
        print("""
==============================================================
          Simple Interactive RC Car Control                   
==============================================================
  Commands (press Enter after each):                          
    w        - Forward                                        
    s        - Backward                                       
    a        - Steer Left                                     
    d        - Steer Right                                    
    stop     - Stop Drive                                     
    space    - Stop Drive (same as stop)                      
    c        - Center Steering                                
    center   - Center Steering (same as c)                    
    x        - All Off                                        
    off      - All Off (same as x)                            
                                                                
    help     - Show this help                                 
    quit     - Quit                                           
    q        - Quit (same as quit)                            
==============================================================
""")
    
    def run(self):
        """Run interactive control loop"""
        mode_str = "LOCAL" if self.is_local else f"REMOTE ({self.pi_host})"
        print(f"\nRunning in {mode_str} mode\n")
        
        self.print_help()
        print("\nType commands and press Enter (or 'help' for commands, 'quit' to exit):\n")
        
        try:
            while self.running:
                try:
                    command = input("RC Car> ").strip().lower()
                    
                    if not command:
                        continue
                    
                    if command in ['q', 'quit', 'exit']:
                        print("Quitting...")
                        break
                    elif command == 'help':
                        self.print_help()
                        continue
                    
                    # Send command
                    print(f"→ Executing: {command}", end='', flush=True)
                    try:
                        self.send_command(command)
                        print(" ✓")
                    except Exception as e:
                        print(f" ✗ Error: {e}")
                    
                except EOFError:
                    # Ctrl+D pressed
                    print("\nQuitting...")
                    break
                except KeyboardInterrupt:
                    # Ctrl+C pressed
                    print("\n\nQuitting...")
                    break
        
        finally:
            # Ensure we stop the car when exiting
            try:
                self.send_command('x')
            except:
                pass
            if self.local_controller:
                self.local_controller.disconnect()
            print("Car stopped. Goodbye!")


def main():
    parser = argparse.ArgumentParser(description='Simple Interactive RC Car Control')
    parser.add_argument('--host', '-H', default=None,
                       help='Raspberry Pi hostname or IP (None = auto-detect local)')
    parser.add_argument('--user', '-u', default='pi',
                       help='SSH username (default: pi)')
    parser.add_argument('--script', '-s', default=None,
                       help='Path to controller script (auto-detected if not provided)')
    parser.add_argument('--service', action='store_true',
                       help='Use file-based service for faster response')
    parser.add_argument('--service-file', default='/tmp/rc_car_command',
                       help='Command file path for service mode')
    parser.add_argument('--arduino-port', '-p', default='/dev/ttyACM0',
                       help='Arduino port for local mode (default: /dev/ttyACM0)')
    parser.add_argument('--arduino-baudrate', '-b', type=int, default=115200,
                       help='Arduino baud rate (default: 115200)')
    parser.add_argument('--local', action='store_true',
                       help='Force local mode (skip SSH)')
    parser.add_argument('--remote', action='store_true',
                       help='Force remote mode (use SSH)')
    
    args = parser.parse_args()
    
    # Determine local mode
    local_mode = None
    if args.local:
        local_mode = True
    elif args.remote:
        local_mode = False
    # Otherwise auto-detect
    
    controller = SimpleInteractiveControl(
        pi_host=args.host,
        pi_user=args.user,
        script_path=args.script,
        use_service=args.service,
        service_file=args.service_file,
        arduino_port=args.arduino_port,
        arduino_baudrate=args.arduino_baudrate,
        local_mode=local_mode
    )
    
    controller.run()


if __name__ == '__main__':
    main()

