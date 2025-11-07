#!/usr/bin/env python3
"""
Interactive RC Car Control
Real-time control script that runs continuously and accepts commands as you type
"""

import sys
import subprocess
import select
import tty
import termios
import argparse
import os
import socket
from typing import Optional

# Try to import the Arduino controller for direct connection
try:
    from arduino_wasd_controller import ArduinoWASDController
    HAS_CONTROLLER = True
except ImportError:
    HAS_CONTROLLER = False


class InteractiveRCCarControl:
    """Interactive real-time RC car controller"""
    
    def __init__(self, pi_host: str = None, pi_user: str = 'pi',
                 script_path: str = None,
                 use_service: bool = False, service_file: str = '/tmp/rc_car_command',
                 arduino_port: str = '/dev/ttyACM0', local_mode: bool = None):
        """
        Initialize interactive controller
        
        Args:
            pi_host: Raspberry Pi hostname or IP (None = auto-detect local)
            pi_user: SSH username
            script_path: Path to controller script on Pi
            use_service: Use file-based service for faster response
            service_file: Command file path for service mode
            arduino_port: Arduino port for local mode
            local_mode: Force local mode (None = auto-detect)
        """
        self.pi_host = pi_host
        self.pi_user = pi_user
        # Auto-detect script path if not provided
        if script_path is None:
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
        self.running = False
        self.old_settings = None
        self.local_controller = None
        
        # Auto-detect if running locally
        if local_mode is None:
            self.is_local = self._detect_local_mode()
        else:
            self.is_local = local_mode
        
        # If running locally and controller available, use direct connection
        if self.is_local and HAS_CONTROLLER and not use_service:
            try:
                self.local_controller = ArduinoWASDController(port=arduino_port)
                if self.local_controller.connect():
                    print(f"Connected directly to Arduino on {arduino_port}")
                else:
                    self.local_controller = None
            except Exception as e:
                print(f"Could not connect directly: {e}")
                self.local_controller = None
    
    def _detect_local_mode(self) -> bool:
        """Detect if we're running on the Pi locally"""
        if self.pi_host is None:
            return True
        try:
            hostname = socket.gethostname()
            if self.pi_host in [hostname, 'localhost', '127.0.0.1', 'raspberrypi', 'raspberrypi.local']:
                if socket.gethostbyname(self.pi_host) in ['127.0.0.1', '::1']:
                    return True
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
                pass
        else:
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
        except:
            pass
    
    def _send_command_ssh(self, command: str):
        """Send command via SSH"""
        ssh_cmd = f'ssh {self.pi_user}@{self.pi_host} "python3 {self.script_path} {command}"'
        try:
            subprocess.run(ssh_cmd, shell=True, stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL, timeout=2)
        except:
            pass
    
    def _send_command_service(self, command: str):
        """Send command via service file (remote)"""
        ssh_cmd = f'ssh {self.pi_user}@{self.pi_host} "echo \\"{command}\\" > {self.service_file}"'
        try:
            subprocess.run(ssh_cmd, shell=True, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, timeout=1)
        except:
            pass
    
    def send_command(self, command: str):
        """Send command to RC car"""
        if self.is_local:
            if self.use_service:
                self._send_command_service_file(command)
            else:
                self._send_command_local(command)
        else:
            if self.use_service:
                self._send_command_service(command)
            else:
                self._send_command_ssh(command)
    
    def setup_terminal(self):
        """Setup terminal for single-character input"""
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
    
    def restore_terminal(self):
        """Restore terminal settings"""
        if self.old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
    
    def print_help(self):
        """Print help message"""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║          Interactive RC Car Control                          ║
╠══════════════════════════════════════════════════════════════╣
║  Controls:                                                    ║
║    W / ↑    - Forward                                        ║
║    S / ↓    - Backward                                       ║
║    A / ←    - Steer Left                                     ║
║    D / →    - Steer Right                                    ║
║    Space    - Stop Drive                                     ║
║    C        - Center Steering                                ║
║    X        - All Off                                        ║
║                                                              ║
║    H        - Show this help                                ║
║    Q        - Quit                                           ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(help_text)
    
    def run(self):
        """Run interactive control loop"""
        self.running = True
        self.setup_terminal()
        
        try:
            self.print_help()
            print("\nPress keys to control (Q to quit, H for help):")
            
            while self.running:
                # Check if input is available
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)
                    
                    # Handle special characters
                    if ord(char) == 27:  # Escape sequence (arrow keys)
                        char = sys.stdin.read(1)
                        if ord(char) == 91:  # [
                            char = sys.stdin.read(1)
                            if ord(char) == 65:  # Up arrow
                                char = 'w'
                            elif ord(char) == 66:  # Down arrow
                                char = 's'
                            elif ord(char) == 67:  # Right arrow
                                char = 'd'
                            elif ord(char) == 68:  # Left arrow
                                char = 'a'
                            else:
                                continue
                    
                    char_lower = char.lower()
                    
                    # Process command
                    if char_lower == 'q':
                        print("\n\nQuitting...")
                        break
                    elif char_lower == 'h':
                        print("\n")
                        self.print_help()
                        print("\nPress keys to control (Q to quit, H for help):")
                        continue
                    elif char_lower == 'w':
                        self.send_command('w')
                        print("→ Forward", end='\r', flush=True)
                    elif char_lower == 's':
                        self.send_command('s')
                        print("→ Backward", end='\r', flush=True)
                    elif char_lower == 'a':
                        self.send_command('a')
                        print("→ Left   ", end='\r', flush=True)
                    elif char_lower == 'd':
                        self.send_command('d')
                        print("→ Right  ", end='\r', flush=True)
                    elif char == ' ':
                        self.send_command(' ')
                        print("→ Stop   ", end='\r', flush=True)
                    elif char_lower == 'c':
                        self.send_command('c')
                        print("→ Center ", end='\r', flush=True)
                    elif char_lower == 'x':
                        self.send_command('x')
                        print("→ All Off", end='\r', flush=True)
        
        except KeyboardInterrupt:
            print("\n\nInterrupted. Stopping...")
        finally:
            # Ensure we stop the car when exiting
            try:
                self.send_command('x')
            except:
                pass
            if self.local_controller:
                self.local_controller.disconnect()
            self.restore_terminal()
            print("\nDisconnected. Car stopped.")


def main():
    parser = argparse.ArgumentParser(description='Interactive RC Car Control')
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
    parser.add_argument('--local', action='store_true',
                       help='Force local mode (skip SSH)')
    parser.add_argument('--remote', action='store_true',
                       help='Force remote mode (use SSH)')
    
    args = parser.parse_args()
    
    local_mode = None
    if args.local:
        local_mode = True
    elif args.remote:
        local_mode = False
    
    controller = InteractiveRCCarControl(
        pi_host=args.host,
        pi_user=args.user,
        script_path=args.script,
        use_service=args.service,
        service_file=args.service_file,
        arduino_port=args.arduino_port,
        local_mode=local_mode
    )
    
    controller.run()


if __name__ == '__main__':
    main()

