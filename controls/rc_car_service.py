"""
RC Car Service - Runs on Raspberry Pi as a background service
Listens for commands via file or network socket
"""

import serial
import time
import os
import sys
import argparse
from pathlib import Path
import socket
import threading


class RCCarService:
    """Service that runs on Raspberry Pi to control Arduino"""
    
    def __init__(self, port: str = '/dev/ttyACM0', baudrate: int = 9600,
                 command_file: str = '/tmp/rc_car_command',
                 socket_port: int = 8888):
        """
        Initialize RC Car Service
        
        Args:
            port: Arduino serial port
            baudrate: Serial baud rate
            command_file: Path to command file for file-based communication
            socket_port: Port for socket-based communication
        """
        self.port = port
        self.baudrate = baudrate
        self.command_file = Path(command_file)
        self.socket_port = socket_port
        self.serial: serial.Serial = None
        self.running = False
        
    def connect_arduino(self):
        """Connect to Arduino"""
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)
            print(f"Connected to Arduino on {self.port}")
            return True
        except Exception as e:
            print(f"Error connecting to Arduino: {e}")
            return False
    
    def disconnect_arduino(self):
        """Disconnect from Arduino"""
        if self.serial:
            self.serial.close()
            self.serial = None
    
    def send_command(self, cmd: str):
        """Send command to Arduino"""
        if not self.serial:
            return "Not connected to Arduino"
        
        cmd_map = {
            'w': 'W', 's': 'S', 'a': 'A', 'd': 'D',
            ' ': ' ', 'space': ' ', 'stop': ' ',
            'c': 'C', 'center': 'C',
            'x': 'X', 'off': 'X'
        }
        
        cmd = cmd.lower().strip()
        arduino_cmd = cmd_map.get(cmd, cmd.upper())
        
        self.serial.write(arduino_cmd.encode())
        time.sleep(0.05)
        
        if self.serial.in_waiting > 0:
            return self.serial.readline().decode().strip()
        return "OK"
    
    def file_based_server(self):
        """File-based command server"""
        print("Starting file-based command server...")
        print(f"Command file: {self.command_file}")
        
        while self.running:
            try:
                if self.command_file.exists():
                    # Read command
                    with open(self.command_file, 'r') as f:
                        command = f.read().strip()
                    
                    # Execute command
                    if command:
                        response = self.send_command(command)
                        print(f"Command: {command} -> {response}")
                    
                    # Remove command file
                    self.command_file.unlink()
                
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in file server: {e}")
                time.sleep(1)
    
    def socket_server(self):
        """Socket-based command server"""
        print(f"Starting socket server on port {self.socket_port}...")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', self.socket_port))
        sock.listen(5)
        sock.settimeout(1.0)
        
        while self.running:
            try:
                client, addr = sock.accept()
                print(f"Connection from {addr}")
                
                # Handle client in a thread
                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.daemon = True
                thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error in socket server: {e}")
                time.sleep(1)
        
        sock.close()
    
    def handle_client(self, client):
        """Handle a client connection"""
        try:
            while True:
                data = client.recv(1024)
                if not data:
                    break
                
                command = data.decode().strip()
                if command == 'quit':
                    break
                
                response = self.send_command(command)
                client.send(f"{response}\n".encode())
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client.close()
    
    def start(self, mode: str = 'file'):
        """Start the service"""
        if not self.connect_arduino():
            return False
        
        self.running = True
        
        try:
            if mode == 'file':
                self.file_based_server()
            elif mode == 'socket':
                self.socket_server()
            elif mode == 'both':
                # Start both servers in separate threads
                file_thread = threading.Thread(target=self.file_based_server)
                socket_thread = threading.Thread(target=self.socket_server)
                file_thread.daemon = True
                socket_thread.daemon = True
                file_thread.start()
                socket_thread.start()
                
                # Keep main thread alive
                while self.running:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.running = False
            self.disconnect_arduino()
        
        return True


def main():
    parser = argparse.ArgumentParser(description='RC Car Service for Raspberry Pi')
    parser.add_argument('--port', '-p', default='/dev/ttyACM0',
                       help='Arduino serial port')
    parser.add_argument('--baudrate', '-b', type=int, default=9600,
                       help='Serial baud rate')
    parser.add_argument('--mode', '-m', choices=['file', 'socket', 'both'], 
                       default='file',
                       help='Communication mode')
    parser.add_argument('--command-file', default='/tmp/rc_car_command',
                       help='Command file path (for file mode)')
    parser.add_argument('--socket-port', type=int, default=8888,
                       help='Socket port (for socket mode)')
    
    args = parser.parse_args()
    
    service = RCCarService(
        port=args.port,
        baudrate=args.baudrate,
        command_file=args.command_file,
        socket_port=args.socket_port
    )
    
    service.start(mode=args.mode)


if __name__ == '__main__':
    main()

