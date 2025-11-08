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
import time
import threading
from typing import Optional

# Try to import the Arduino controller for direct connection
try:
    from arduino_wasd_controller import ArduinoWASDController
    HAS_CONTROLLER = True
except ImportError:
    HAS_CONTROLLER = False

# Try to import keyboard library for proper key release detection
try:
    import keyboard
    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False

# Try to import motor monitor
try:
    from motor_monitor import MotorMonitor
    HAS_MONITOR = True
except ImportError:
    HAS_MONITOR = False
    MotorMonitor = None


class InteractiveRCCarControl:
    """Interactive real-time RC car controller"""
    
    def __init__(self, pi_host: str = None, pi_user: str = 'pi',
                 script_path: str = None,
                 use_service: bool = False, service_file: str = '/tmp/rc_car_command',
                 arduino_port: str = '/dev/ttyACM0', arduino_baudrate: int = 115200, local_mode: bool = None,
                 enable_monitor: bool = False):
        """
        Initialize interactive controller
        
        Args:
            pi_host: Raspberry Pi hostname or IP (None = auto-detect local)
            pi_user: SSH username
            script_path: Path to controller script on Pi
            use_service: Use file-based service for faster response
            service_file: Command file path for service mode
            arduino_port: Arduino port for local mode
            arduino_baudrate: Arduino baud rate (default: 115200)
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
        self.arduino_baudrate = arduino_baudrate
        self.running = False
        self.old_settings = None
        self.local_controller = None
        self.enable_monitor = enable_monitor
        self.monitor = None
        
        # Initialize monitor if enabled
        if enable_monitor and HAS_MONITOR:
            self.monitor = MotorMonitor()
        
        # Auto-detect if running locally
        if local_mode is None:
            self.is_local = self._detect_local_mode()
        else:
            self.is_local = local_mode
        
        # If running locally and controller available, use direct connection
        if self.is_local and HAS_CONTROLLER and not use_service:
            try:
                self.local_controller = ArduinoWASDController(port=arduino_port, baudrate=arduino_baudrate, debug=False)
                if self.local_controller.connect(debug=False):
                    print(f"Connected directly to Arduino on {arduino_port} at {arduino_baudrate} baud")
                else:
                    print("WARNING: Could not connect to Arduino, commands may not work")
                    self.local_controller = None
            except Exception as e:
                print(f"WARNING: Could not connect directly: {e}")
                print("Commands will be sent but may not execute")
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
                response = self.local_controller.execute_command(command, debug=False)
                # Response is optional - command may execute even if no response
                return response
            except Exception as e:
                # Don't print errors for every command (too noisy)
                # But log them if monitor is enabled
                if self.monitor:
                    import traceback
                    traceback.print_exc()
                return None
        else:
            script_path = os.path.expanduser(self.script_path)
            if os.path.exists(script_path):
                try:
                    result = subprocess.run(
                        ['python3', script_path, command],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=2
                    )
                    return result.stdout.decode('utf-8', errors='ignore').strip()
                except Exception:
                    return None
        return None
    
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
        # Log command to monitor if enabled
        if self.monitor:
            start_time = time.time()
            try:
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
                response_time = time.time() - start_time
                self.monitor.log_command(command, response_time=response_time, success=True)
            except Exception as e:
                response_time = time.time() - start_time
                self.monitor.log_command(command, response_time=response_time, success=False, error=str(e))
                raise
        else:
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
==============================================================
          Interactive RC Car Control                          
==============================================================
  Controls:                                                    
    W               - Forward                                
    S               - Backward                               
    A               - Steer Left                             
    D               - Steer Right                            
    Space           - Stop Drive                             
    C               - Center Steering                        
    X               - All Off                                
                                                                
    H               - Show this help                         
    Q               - Quit                                   
==============================================================
"""
        print(help_text)
    
    def run(self):
        """Run interactive control loop"""
        # On Linux/Raspberry Pi, keyboard library requires root, so prefer terminal mode
        # Terminal mode works well without root and handles WASD keys properly
        # Only use keyboard library if it's available AND we have root OR we're on macOS/Windows
        try:
            is_root = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
            is_linux = sys.platform == 'linux'
            use_keyboard = HAS_KEYBOARD and (not is_linux or is_root)
        except:
            use_keyboard = False
        
        if use_keyboard:
            try:
                self._run_with_keyboard()
                return
            except Exception as e:
                print(f"Keyboard library failed: {e}")
                print("Falling back to terminal mode...\n")
        
        # Use terminal mode (works on all platforms, no root required)
        self._run_with_terminal()
    
    def _run_with_keyboard(self):
        """Run with keyboard library for proper key release detection"""
        self.running = True
        
        # Check if we have proper permissions (keyboard library needs root on Linux)
        try:
            # Test if we can hook a key
            test_hook = keyboard.on_press_key('q', lambda _: None)
            keyboard.unhook(test_hook)
        except Exception as e:
            print(f"Warning: Keyboard library may need root privileges. Error: {e}")
            print("Falling back to terminal mode...\n")
            self.restore_terminal()
            self._run_with_terminal()
            return
        
        self.print_help()
        print("\nPress and HOLD keys (release to stop drive):")
        print("Note: Keyboard library is active for auto-stop\n")
        
        # Track active drive command
        active_drive = None
        
        # Key press handlers
        def on_w_press(_):
            nonlocal active_drive
            if active_drive != 'w':
                self.send_command('w')
                active_drive = 'w'
                print("Forward", end='\r', flush=True)
        
        def on_w_release(_):
            nonlocal active_drive
            if active_drive == 'w':
                self.send_command(' ')  # Stop drive
                active_drive = None
                print("Stopped", end='\r', flush=True)
        
        def on_s_press(_):
            nonlocal active_drive
            if active_drive != 's':
                self.send_command('s')
                active_drive = 's'
                print("Backward", end='\r', flush=True)
        
        def on_s_release(_):
            nonlocal active_drive
            if active_drive == 's':
                self.send_command(' ')  # Stop drive
                active_drive = None
                print("Stopped", end='\r', flush=True)
        
        def on_a_press(_):
            self.send_command('a')
            print("Left", end='\r', flush=True)
        
        def on_d_press(_):
            self.send_command('d')
            print("Right", end='\r', flush=True)
        
        # Register keyboard hooks (WASD keys only)
        keyboard.on_press_key('w', on_w_press)
        keyboard.on_release_key('w', on_w_release)
        keyboard.on_press_key('s', on_s_press)
        keyboard.on_release_key('s', on_s_release)
        keyboard.on_press_key('a', on_a_press)
        keyboard.on_press_key('d', on_d_press)
        
        def on_space_press(_):
            nonlocal active_drive
            if active_drive:
                self.send_command(' ')
                active_drive = None
                print("Stop Drive", end='\r', flush=True)
        
        def on_c_press(_):
            self.send_command('c')
            print("Center Steering", end='\r', flush=True)
        
        def on_x_press(_):
            nonlocal active_drive
            if active_drive:
                self.send_command(' ')
                active_drive = None
            self.send_command('x')
            print("All Off", end='\r', flush=True)
        
        keyboard.on_press_key('space', on_space_press)
        keyboard.on_press_key('c', on_c_press)
        keyboard.on_press_key('x', on_x_press)
        
        try:
            print("Press 'Q' to quit\n")
            keyboard.wait('q')
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"\nError with keyboard library: {e}")
            print("Falling back to terminal mode...")
            keyboard.unhook_all()
            self._run_with_terminal()
            return
        finally:
            self.running = False
            try:
                keyboard.unhook_all()
            except:
                pass
            if active_drive:
                self.send_command(' ')
            self.send_command('x')
            if self.local_controller:
                self.local_controller.disconnect()
            if self.monitor:
                print("\n" + self.monitor.get_summary())
                self.monitor.end_session()
            print("\nDisconnected. Car stopped.")
    
    def _run_with_terminal(self):
        """Run with terminal input (fallback when keyboard library not available)"""
        self.running = True
        
        # Only setup terminal if we haven't already (prevents double setup)
        if self.old_settings is None:
            self.setup_terminal()
        
        try:
            self.print_help()
            print("\nPress keys for control (Q to quit, H for help):")
            print("Note: Drive (W/S) is latched - press Space to stop")
            print("Tip: Press and hold W/S, then release and press Space to stop")
            print("Waiting for input...\n")
            
            # Track last drive command
            last_drive_command = None
            last_input_time = time.time()
            auto_stop_timeout = 5.0  # Auto-stop after 5 seconds of no input (safety only)
            
            while self.running:
                current_time = time.time()
                input_available = False
                char = None
                
                # Check if input is available (non-blocking)
                try:
                    ready, _, _ = select.select([sys.stdin], [], [], 0.1)
                    if ready:
                        input_available = True
                        char = sys.stdin.read(1)
                        last_input_time = current_time
                        
                        # Handle escape sequences (arrow keys convert to WASD)
                        if char and ord(char) == 27:  # Escape sequence
                            try:
                                char2 = sys.stdin.read(1)
                                if ord(char2) == 91:  # [
                                    char3 = sys.stdin.read(1)
                                    if ord(char3) == 65:  # Up arrow
                                        char = 'w'
                                    elif ord(char3) == 66:  # Down arrow
                                        char = 's'
                                    elif ord(char3) == 67:  # Right arrow
                                        char = 'd'
                                    elif ord(char3) == 68:  # Left arrow
                                        char = 'a'
                                    else:
                                        char = None
                                        input_available = False
                                else:
                                    char = None
                                    input_available = False
                            except (OSError, ValueError, IndexError):
                                char = None
                                input_available = False
                except (OSError, ValueError) as e:
                    # Terminal might be closed or invalid
                    print(f"\nTerminal error: {e}")
                    break
                
                # Process input
                if input_available and char:
                    # Skip null bytes and other control characters
                    try:
                        if ord(char) == 0:
                            continue
                    except (TypeError, ValueError):
                        continue
                    
                    char_lower = char.lower()
                    
                    if char_lower == 'q':
                        print("\n\nQuitting...")
                        if last_drive_command:
                            self.send_command(' ')
                        self.running = False
                        break
                    elif char_lower == 'h':
                        print("\n")
                        self.print_help()
                        print("\nPress keys for control (Q to quit, H for help):")
                        print("Note: Drive (W/S) is latched - press Space to stop\n")
                        last_drive_command = None
                        continue
                    elif char_lower == 'w':
                        if last_drive_command != 'w':
                            self.send_command('w')
                            last_drive_command = 'w'
                            print("Forward (press Space to stop)", end='\r', flush=True)
                    elif char_lower == 's':
                        if last_drive_command != 's':
                            self.send_command('s')
                            last_drive_command = 's'
                            print("Backward (press Space to stop)", end='\r', flush=True)
                    elif char_lower == 'a':
                        self.send_command('a')
                        print("Left", end='\r', flush=True)
                    elif char_lower == 'd':
                        self.send_command('d')
                        print("Right", end='\r', flush=True)
                    elif char == ' ':
                        if last_drive_command:
                            self.send_command(' ')
                            last_drive_command = None
                            print("Stop Drive", end='\r', flush=True)
                    elif char_lower == 'c':
                        self.send_command('c')
                        print("Center Steering", end='\r', flush=True)
                    elif char_lower == 'x':
                        if last_drive_command:
                            self.send_command(' ')
                            last_drive_command = None
                        self.send_command('x')
                        print("All Off", end='\r', flush=True)
                
                # Auto-stop drive if no input detected for a while (safety feature only)
                # Note: Users should press Space to stop manually
                # This is just a safety timeout to prevent the car from running indefinitely
                if last_drive_command and (current_time - last_input_time >= auto_stop_timeout):
                    self.send_command(' ')
                    last_drive_command = None
                    print("Auto-stopped (safety timeout)", end='\r', flush=True)
                    time.sleep(0.2)
                    print("Ready - press keys (W/S/A/D, Space=stop, Q=quit)", end='\r', flush=True)
                    last_input_time = current_time + 1.0  # Reset to prevent repeated stops
        
        except KeyboardInterrupt:
            print("\n\nInterrupted. Stopping...")
        finally:
            # Ensure we stop the car when exiting
            try:
                if last_drive_command:
                    self.send_command(' ')
                self.send_command('x')
            except:
                pass
            if self.local_controller:
                self.local_controller.disconnect()
            if self.monitor:
                print("\n" + self.monitor.get_summary())
                self.monitor.end_session()
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
    parser.add_argument('--arduino-baudrate', '-b', type=int, default=115200,
                       help='Arduino baud rate (default: 115200)')
    parser.add_argument('--local', action='store_true',
                       help='Force local mode (skip SSH)')
    parser.add_argument('--remote', action='store_true',
                       help='Force remote mode (use SSH)')
    parser.add_argument('--monitor', '-m', action='store_true',
                       help='Enable motor monitoring and benchmarking')
    
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
        arduino_baudrate=args.arduino_baudrate,
        local_mode=local_mode,
        enable_monitor=args.monitor
    )
    
    controller.run()


if __name__ == '__main__':
    main()

