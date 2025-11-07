"""
RC Car Client - Laptop-side script to send commands via SSH to Raspberry Pi
"""

import subprocess
import sys
import argparse


class RCCarClient:
    """Client for sending RC car commands via SSH to Raspberry Pi"""
    
    def __init__(self, pi_host: str, pi_user: str = 'pi', 
                 script_path: str = '~/rc_car_control/arduino_wasd_controller.py'):
        """
        Initialize RC Car Client
        
        Args:
            pi_host: Raspberry Pi hostname or IP address
            pi_user: Username on Raspberry Pi (default: 'pi')
            script_path: Path to controller script on Raspberry Pi
        """
        self.pi_host = pi_host
        self.pi_user = pi_user
        self.script_path = script_path
    
    def _send_ssh_command(self, command: str) -> tuple:
        """
        Send command via SSH to Raspberry Pi
        
        Args:
            command: Command to execute on Raspberry Pi
        
        Returns:
            Tuple of (returncode, stdout, stderr)
        """
        ssh_command = f'ssh {self.pi_user}@{self.pi_host} "python3 {self.script_path} {command}"'
        
        try:
            result = subprocess.run(
                ssh_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    def forward(self):
        """Move forward"""
        return self._send_ssh_command('w')
    
    def backward(self):
        """Move backward"""
        return self._send_ssh_command('s')
    
    def left(self):
        """Steer left"""
        return self._send_ssh_command('a')
    
    def right(self):
        """Steer right"""
        return self._send_ssh_command('d')
    
    def stop(self):
        """Stop drive"""
        return self._send_ssh_command('space')
    
    def center(self):
        """Center steering"""
        return self._send_ssh_command('c')
    
    def all_off(self):
        """Turn everything off"""
        return self._send_ssh_command('x')
    
    def execute(self, command: str):
        """Execute a command"""
        return self._send_ssh_command(command)


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='RC Car Client - Send commands via SSH')
    parser.add_argument('--host', '-H', required=True,
                       help='Raspberry Pi hostname or IP address')
    parser.add_argument('--user', '-u', default='pi',
                       help='SSH username (default: pi)')
    parser.add_argument('--script', '-s', default='~/rc_car_control/arduino_wasd_controller.py',
                       help='Path to controller script on Raspberry Pi')
    parser.add_argument('command', 
                       choices=['w', 's', 'a', 'd', 'space', 'stop', 'c', 'center', 'x', 'off'],
                       help='Command to execute')
    
    args = parser.parse_args()
    
    client = RCCarClient(pi_host=args.host, pi_user=args.user, script_path=args.script)
    
    returncode, stdout, stderr = client.execute(args.command)
    
    if stdout:
        print(stdout, end='')
    if stderr:
        print(stderr, end='', file=sys.stderr)
    
    sys.exit(returncode)


if __name__ == '__main__':
    main()

