#!/usr/bin/env python3
"""
Continuous RC Car Control
Press and hold keys for continuous movement - release to stop
Uses keyboard event detection for proper key press/release handling
"""

import sys
import time
import threading
from typing import Dict, Optional
import os

# Try to import keyboard library for better key detection
try:
    import keyboard
    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False
    print("Note: 'keyboard' library not installed. Install with: pip3 install keyboard")
    print("Falling back to basic input mode...")

# Try to import the Arduino controller
try:
    from arduino_wasd_controller import ArduinoWASDController
    HAS_CONTROLLER = True
except ImportError:
    HAS_CONTROLLER = False


class ContinuousRCCarControl:
    """Continuous control with key press/release detection"""
    
    def __init__(self, arduino_port: str = '/dev/ttyACM0', 
                 script_path: str = None):
        self.arduino_port = arduino_port
        self.script_path = script_path
        self.controller: Optional[ArduinoWASDController] = None
        self.running = False
        self.active_commands: Dict[str, bool] = {
            'w': False,  # Forward
            's': False,  # Backward
            'a': False,  # Left
            'd': False,  # Right
        }
        self.command_thread = None
        
        # Initialize controller
        if HAS_CONTROLLER:
            try:
                self.controller = ArduinoWASDController(port=arduino_port)
                if self.controller.connect():
                    print(f"Connected to Arduino on {arduino_port}")
                else:
                    self.controller = None
            except Exception as e:
                print(f"Could not connect to Arduino: {e}")
                self.controller = None
    
    def send_command(self, cmd: str):
        """Send command to Arduino"""
        if self.controller:
            try:
                self.controller.execute_command(cmd)
            except Exception as e:
                print(f"Error: {e}")
        else:
            # Fallback to script execution
            if self.script_path and os.path.exists(self.script_path):
                import subprocess
                subprocess.run(['python3', self.script_path, cmd], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    def start_command(self, cmd: str):
        """Start a continuous command"""
        if cmd in self.active_commands:
            self.active_commands[cmd] = True
            self.send_command(cmd)
    
    def stop_command(self, cmd: str):
        """Stop a continuous command"""
        if cmd in self.active_commands:
            self.active_commands[cmd] = False
            # Send stop command
            if cmd in ['w', 's']:
                self.send_command(' ')  # Stop drive
            elif cmd in ['a', 'd']:
                self.send_command('c')  # Center steering
    
    def stop_all(self):
        """Stop all commands"""
        for cmd in list(self.active_commands.keys()):
            self.active_commands[cmd] = False
        self.send_command('x')  # All off
    
    def command_loop(self):
        """Continuously send active commands"""
        while self.running:
            for cmd, active in self.active_commands.items():
                if active:
                    self.send_command(cmd)
            time.sleep(0.1)  # Send commands every 100ms
    
    def run_keyboard(self):
        """Run with keyboard library for proper key detection"""
        if not HAS_KEYBOARD:
            print("keyboard library not available")
            return False
        
        print("""
╔══════════════════════════════════════════════════════════════╗
║          Continuous RC Car Control                           ║
╠══════════════════════════════════════════════════════════════╣
║  Press and HOLD keys (release to stop):                       ║
║    W / ↑    - Forward (hold to keep moving)                   ║
║    S / ↓    - Backward (hold to keep moving)                  ║
║    A / ←    - Steer Left (hold to keep turning)               ║
║    D / →    - Steer Right (hold to keep turning)              ║
║                                                              ║
║    Space    - Stop Drive                                      ║
║    C        - Center Steering                                 ║
║    X        - All Off                                         ║
║    Q        - Quit                                            ║
╚══════════════════════════════════════════════════════════════╝
""")
        print("Press keys to control (Q to quit)...\n")
        
        self.running = True
        self.command_thread = threading.Thread(target=self.command_loop, daemon=True)
        self.command_thread.start()
        
        # Set up keyboard hooks
        keyboard.on_press_key('w', lambda _: self.start_command('w'))
        keyboard.on_release_key('w', lambda _: self.stop_command('w'))
        keyboard.on_press_key('s', lambda _: self.start_command('s'))
        keyboard.on_release_key('s', lambda _: self.stop_command('s'))
        keyboard.on_press_key('a', lambda _: self.start_command('a'))
        keyboard.on_release_key('a', lambda _: self.stop_command('a'))
        keyboard.on_press_key('d', lambda _: self.start_command('d'))
        keyboard.on_release_key('d', lambda _: self.stop_command('d'))
        
        keyboard.on_press_key('up', lambda _: self.start_command('w'))
        keyboard.on_release_key('up', lambda _: self.stop_command('w'))
        keyboard.on_press_key('down', lambda _: self.start_command('s'))
        keyboard.on_release_key('down', lambda _: self.stop_command('s'))
        keyboard.on_press_key('left', lambda _: self.start_command('a'))
        keyboard.on_release_key('left', lambda _: self.stop_command('a'))
        keyboard.on_press_key('right', lambda _: self.start_command('d'))
        keyboard.on_release_key('right', lambda _: self.stop_command('d'))
        
        keyboard.on_press_key('space', lambda _: self.send_command(' '))
        keyboard.on_press_key('c', lambda _: self.send_command('c'))
        keyboard.on_press_key('x', lambda _: self.stop_all())
        
        try:
            keyboard.wait('q')
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            self.stop_all()
            if self.controller:
                self.controller.disconnect()
            print("\nStopped. Goodbye!")
    
    def run_basic(self):
        """Run with basic input (fallback)"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║          Continuous RC Car Control (Basic Mode)              ║
╠══════════════════════════════════════════════════════════════╣
║  Type commands and press Enter:                              ║
║    w+       - Start Forward (continuous)                     ║
║    w-       - Stop Forward                                   ║
║    s+       - Start Backward (continuous)                     ║
║    s-       - Stop Backward                                  ║
║    a+       - Start Left (continuous)                        ║
║    a-       - Stop Left                                      ║
║    d+       - Start Right (continuous)                       ║
║    d-       - Stop Right                                     ║
║                                                              ║
║    stop     - Stop Drive                                     ║
║    center   - Center Steering                                ║
║    off      - All Off                                        ║
║    quit     - Quit                                           ║
╚══════════════════════════════════════════════════════════════╝
""")
        
        self.running = True
        self.command_thread = threading.Thread(target=self.command_loop, daemon=True)
        self.command_thread.start()
        
        try:
            while self.running:
                cmd = input("RC Car> ").strip().lower()
                
                if cmd == 'quit' or cmd == 'q':
                    break
                elif cmd == 'w+':
                    self.start_command('w')
                    print("Forward started (hold)")
                elif cmd == 'w-':
                    self.stop_command('w')
                    print("Forward stopped")
                elif cmd == 's+':
                    self.start_command('s')
                    print("Backward started (hold)")
                elif cmd == 's-':
                    self.stop_command('s')
                    print("Backward stopped")
                elif cmd == 'a+':
                    self.start_command('a')
                    print("Left started (hold)")
                elif cmd == 'd+':
                    self.start_command('d')
                    print("Right started (hold)")
                elif cmd == 'a-':
                    self.stop_command('a')
                    print("Left stopped")
                elif cmd == 'd-':
                    self.stop_command('d')
                    print("Right stopped")
                elif cmd == 'stop':
                    self.send_command(' ')
                elif cmd == 'center':
                    self.send_command('c')
                elif cmd == 'off':
                    self.stop_all()
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            self.stop_all()
            if self.controller:
                self.controller.disconnect()
            print("\nStopped. Goodbye!")
    
    def run(self):
        """Run the controller"""
        if HAS_KEYBOARD:
            self.run_keyboard()
        else:
            self.run_basic()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Continuous RC Car Control')
    parser.add_argument('--port', '-p', default='/dev/ttyACM0',
                       help='Arduino port')
    parser.add_argument('--script', '-s', default=None,
                       help='Path to controller script')
    
    args = parser.parse_args()
    
    controller = ContinuousRCCarControl(
        arduino_port=args.port,
        script_path=args.script
    )
    
    controller.run()


if __name__ == '__main__':
    main()

