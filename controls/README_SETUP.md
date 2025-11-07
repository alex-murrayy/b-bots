# RC Car Remote Control Setup Guide

This guide explains how to set up remote control of your RC car Arduino from your laptop via SSH through a Raspberry Pi.

## Architecture

```
Laptop (SSH) → Raspberry Pi → Arduino (Serial) → Motor Driver → Motors
```

## Components

1. **Arduino Sketch**: Your existing WASD control sketch (already working)
2. **Raspberry Pi Controller**: `arduino_wasd_controller.py` - Sends commands to Arduino
3. **RC Car Service** (optional): `rc_car_service.py` - Background service on Pi
4. **Laptop Client**: `rc_car_client.py` - Send commands via SSH

## Setup on Raspberry Pi

### 1. Install Dependencies

```bash
pip3 install pyserial
```

### 2. Copy Files to Raspberry Pi

From your laptop, copy the controller script to your Raspberry Pi:

```bash
scp controls/arduino_wasd_controller.py pi@raspberrypi.local:~/rc_car_control/
scp controls/rc_car_service.py pi@raspberrypi.local:~/rc_car_control/
```

Or create the directory and copy manually:
```bash
ssh pi@raspberrypi.local "mkdir -p ~/rc_car_control"
```

### 3. Find Arduino Port

On the Raspberry Pi, find which port the Arduino is connected to:

```bash
python3 ~/rc_car_control/arduino_wasd_controller.py --list-ports
```

Common ports:
- `/dev/ttyACM0` (most common for Arduino Uno)
- `/dev/ttyUSB0` (if using USB-to-serial adapter)

### 4. Test Connection

Test the connection directly on the Raspberry Pi:

```bash
python3 ~/rc_car_control/arduino_wasd_controller.py -p /dev/ttyACM0 -i
```

This will start interactive mode. Try commands: `w`, `s`, `a`, `d`, `space`, `c`, `x`

## Usage Methods

### Method 1: Direct SSH Command Execution (Simplest)

From your laptop, send commands directly:

```bash
# Forward
ssh pi@raspberrypi.local "python3 ~/rc_car_control/arduino_wasd_controller.py w"

# Backward
ssh pi@raspberrypi.local "python3 ~/rc_car_control/arduino_wasd_controller.py s"

# Left
ssh pi@raspberrypi.local "python3 ~/rc_car_control/arduino_wasd_controller.py a"

# Right
ssh pi@raspberrypi.local "python3 ~/rc_car_control/arduino_wasd_controller.py d"

# Stop
ssh pi@raspberrypi.local "python3 ~/rc_car_control/arduino_wasd_controller.py space"

# Center steering
ssh pi@raspberrypi.local "python3 ~/rc_car_control/arduino_wasd_controller.py c"

# All off
ssh pi@raspberrypi.local "python3 ~/rc_car_control/arduino_wasd_controller.py x"
```

### Method 2: Using the Client Script

On your laptop, use the client script:

```bash
# Forward
python3 controls/rc_car_client.py --host raspberrypi.local w

# Backward
python3 controls/rc_car_client.py --host raspberrypi.local s

# Left
python3 controls/rc_car_client.py --host raspberrypi.local a

# Right
python3 controls/rc_car_client.py --host raspberrypi.local d

# Stop
python3 controls/rc_car_client.py --host raspberrypi.local stop

# Center
python3 controls/rc_car_client.py --host raspberrypi.local center

# All off
python3 controls/rc_car_client.py --host raspberrypi.local off
```

### Method 3: Background Service (Recommended for Continuous Use)

Set up a background service on the Raspberry Pi that listens for commands:

#### 3.1 Start the Service

```bash
# On Raspberry Pi
python3 ~/rc_car_control/rc_car_service.py --mode file --port /dev/ttyACM0
```

#### 3.2 Send Commands via File

From your laptop:
```bash
# Forward
ssh pi@raspberrypi.local "echo 'w' > /tmp/rc_car_command"

# Backward
ssh pi@raspberrypi.local "echo 's' > /tmp/rc_car_command"

# Left
ssh pi@raspberrypi.local "echo 'a' > /tmp/rc_car_command"

# Right
ssh pi@raspberrypi.local "echo 'd' > /tmp/rc_car_command"

# Stop
ssh pi@raspberrypi.local "echo 'space' > /tmp/rc_car_command"

# Center
ssh pi@raspberrypi.local "echo 'c' > /tmp/rc_car_command"

# All off
ssh pi@raspberrypi.local "echo 'x' > /tmp/rc_car_command"
```

#### 3.3 Set Up as Systemd Service (Auto-start)

```bash
# On Raspberry Pi
sudo nano /etc/systemd/system/rc-car.service
```

Add:
```ini
[Unit]
Description=RC Car Control Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/rc_car_control
ExecStart=/usr/bin/python3 /home/pi/rc_car_control/rc_car_service.py --mode file --port /dev/ttyACM0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable rc-car.service
sudo systemctl start rc-car.service
sudo systemctl status rc-car.service
```

## Creating Convenient Aliases

On your laptop, add these to your `~/.bashrc` or `~/.zshrc`:

```bash
# RC Car Control Aliases
alias rccar-forward='ssh pi@raspberrypi.local "python3 ~/rc_car_control/arduino_wasd_controller.py w"'
alias rccar-backward='ssh pi@raspberrypi.local "python3 ~/rc_car_control/arduino_wasd_controller.py s"'
alias rccar-left='ssh pi@raspberrypi.local "python3 ~/rc_car_control/arduino_wasd_controller.py a"'
alias rccar-right='ssh pi@raspberrypi.local "python3 ~/rc_car_control/arduino_wasd_controller.py d"'
alias rccar-stop='ssh pi@raspberrypi.local "python3 ~/rc_car_control/arduino_wasd_controller.py space"'
alias rccar-center='ssh pi@raspberrypi.local "python3 ~/rc_car_control/arduino_wasd_controller.py c"'
alias rccar-off='ssh pi@raspberrypi.local "python3 ~/rc_car_control/arduino_wasd_controller.py x"'
```

Then use:
```bash
rccar-forward
rccar-left
rccar-stop
```

## Troubleshooting

### Arduino Not Found
- Check USB connection
- Check permissions: `sudo usermod -a -G dialout $USER` (logout/login)
- List ports: `python3 arduino_wasd_controller.py --list-ports`

### SSH Connection Issues
- Ensure SSH is enabled on Raspberry Pi: `sudo systemctl enable ssh`
- Check network connectivity: `ping raspberrypi.local`
- Use IP address instead of hostname if DNS doesn't work

### Permission Denied
- Add user to dialout group: `sudo usermod -a -G dialout $USER`
- Log out and log back in

### Commands Not Working
- Check Arduino serial monitor to verify commands are received
- Test directly on Raspberry Pi first
- Check baud rate matches (9600)

## Integration with Delivery System

You can integrate this with your Python delivery system:

```python
from controls.arduino_wasd_controller import ArduinoWASDController
import subprocess

class RemoteRCCarController:
    def __init__(self, pi_host='raspberrypi.local', pi_user='pi'):
        self.pi_host = pi_host
        self.pi_user = pi_user
        self.script_path = '~/rc_car_control/arduino_wasd_controller.py'
    
    def _execute(self, command):
        cmd = f'ssh {self.pi_user}@{self.pi_host} "python3 {self.script_path} {command}"'
        subprocess.run(cmd, shell=True)
    
    def forward(self):
        self._execute('w')
    
    def backward(self):
        self._execute('s')
    
    def left(self):
        self._execute('a')
    
    def right(self):
        self._execute('d')
    
    def stop(self):
        self._execute('space')
    
    def center(self):
        self._execute('c')
```

## Security Notes

- Use SSH keys instead of passwords for better security
- Consider using a VPN if accessing over the internet
- Limit SSH access to trusted networks
- Use a non-standard SSH port if exposed to internet

