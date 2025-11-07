#!/usr/bin/env python3
"""
Simple Interactive RC Car Control
Easier version that works without special terminal setup
Just type commands and press Enter
"""

import sys
import subprocess
import argparse
import threading
import time


class SimpleInteractiveControl:
    """Simple interactive controller - type commands and press Enter"""
    
    def __init__(self, pi_host: str = 'raspberrypi.local', pi_user: str = 'pi',
                 script_path: str = '~/rc_car_control/arduino_wasd_controller.py',
                 use_service: bool = False, service_file: str = '/tmp/rc_car_command'):
        self.pi_host = pi_host
        self.pi_user = pi_user
        self.script_path = script_path
        self.use_service = use_service
        self.service_file = service_file
        self.running = True
    
    def _send_command_ssh(self, command: str):
        """Send command via SSH"""
        ssh_cmd = f'ssh {self.pi_user}@{self.pi_host} "python3 {self.script_path} {command}"'
        subprocess.run(ssh_cmd, shell=True, stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, timeout=2)
    
    def _send_command_service(self, command: str):
        """Send command via service file"""
        ssh_cmd = f'ssh {self.pi_user}@{self.pi_host} "echo \\"{command}\\" > {self.service_file}"'
        subprocess.run(ssh_cmd, shell=True, stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL, timeout=1)
    
    def send_command(self, command: str):
        """Send command to RC car"""
        if self.use_service:
            self._send_command_service(command)
        else:
            self._send_command_ssh(command)
    
    def print_help(self):
        """Print help message"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║          Simple Interactive RC Car Control                   ║
╠══════════════════════════════════════════════════════════════╣
║  Commands (press Enter after each):                          ║
║    w        - Forward                                        ║
║    s        - Backward                                       ║
║    a        - Steer Left                                     ║
║    d        - Steer Right                                    ║
║    stop     - Stop Drive                                     ║
║    space    - Stop Drive (same as stop)                      ║
║    c        - Center Steering                                ║
║    center   - Center Steering (same as c)                    ║
║    x        - All Off                                        ║
║    off      - All Off (same as x)                            ║
║                                                              ║
║    help     - Show this help                                ║
║    quit     - Quit                                           ║
║    q        - Quit (same as quit)                            ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    def run(self):
        """Run interactive control loop"""
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
                    self.send_command(command)
                    print(" ✓")
                    
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
            self.send_command('x')
            print("Car stopped. Goodbye!")


def main():
    parser = argparse.ArgumentParser(description='Simple Interactive RC Car Control')
    parser.add_argument('--host', '-H', default='raspberrypi.local',
                       help='Raspberry Pi hostname or IP (default: raspberrypi.local)')
    parser.add_argument('--user', '-u', default='pi',
                       help='SSH username (default: pi)')
    parser.add_argument('--script', '-s', default='~/rc_car_control/arduino_wasd_controller.py',
                       help='Path to controller script on Pi')
    parser.add_argument('--service', action='store_true',
                       help='Use file-based service for faster response')
    parser.add_argument('--service-file', default='/tmp/rc_car_command',
                       help='Command file path for service mode')
    
    args = parser.parse_args()
    
    controller = SimpleInteractiveControl(
        pi_host=args.host,
        pi_user=args.user,
        script_path=args.script,
        use_service=args.service,
        service_file=args.service_file
    )
    
    controller.run()


if __name__ == '__main__':
    main()

