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
from typing import Optional


class InteractiveRCCarControl:
    """Interactive real-time RC car controller"""
    
    def __init__(self, pi_host: str = 'raspberrypi.local', pi_user: str = 'pi',
                 script_path: str = '~/rc_car_control/arduino_wasd_controller.py',
                 use_service: bool = False, service_file: str = '/tmp/rc_car_command'):
        """
        Initialize interactive controller
        
        Args:
            pi_host: Raspberry Pi hostname or IP
            pi_user: SSH username
            script_path: Path to controller script on Pi
            use_service: Use file-based service for faster response
            service_file: Command file path for service mode
        """
        self.pi_host = pi_host
        self.pi_user = pi_user
        self.script_path = script_path
        self.use_service = use_service
        self.service_file = service_file
        self.running = False
        self.old_settings = None
    
    def _send_command_ssh(self, command: str):
        """Send command via SSH"""
        ssh_cmd = f'ssh {self.pi_user}@{self.pi_host} "python3 {self.script_path} {command}"'
        try:
            subprocess.run(ssh_cmd, shell=True, stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL, timeout=2)
        except subprocess.TimeoutExpired:
            pass
    
    def _send_command_service(self, command: str):
        """Send command via service file"""
        ssh_cmd = f'ssh {self.pi_user}@{self.pi_host} "echo \\"{command}\\" > {self.service_file}"'
        try:
            subprocess.run(ssh_cmd, shell=True, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, timeout=1)
        except subprocess.TimeoutExpired:
            pass
    
    def send_command(self, command: str):
        """Send command to RC car"""
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
            self.send_command('x')
            self.restore_terminal()
            print("\nDisconnected. Car stopped.")


def main():
    parser = argparse.ArgumentParser(description='Interactive RC Car Control')
    parser.add_argument('--host', '-H', default='raspberrypi.local',
                       help='Raspberry Pi hostname or IP (default: raspberrypi.local)')
    parser.add_argument('--user', '-u', default='pi',
                       help='SSH username (default: pi)')
    parser.add_argument('--script', '-s', default='~/rc_car_control/arduino_wasd_controller.py',
                       help='Path to controller script on Pi')
    parser.add_argument('--service', action='store_true',
                       help='Use file-based service for faster response (requires rc_car_service.py running)')
    parser.add_argument('--service-file', default='/tmp/rc_car_command',
                       help='Command file path for service mode (default: /tmp/rc_car_command)')
    
    args = parser.parse_args()
    
    controller = InteractiveRCCarControl(
        pi_host=args.host,
        pi_user=args.user,
        script_path=args.script,
        use_service=args.service,
        service_file=args.service_file
    )
    
    controller.run()


if __name__ == '__main__':
    main()

