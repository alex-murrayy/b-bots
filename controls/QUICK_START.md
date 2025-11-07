# Quick Start - Interactive RC Car Control

## Two Interactive Options

### Option 1: Real-Time Key Controls (Recommended)
Press keys without Enter - works like a game controller!

```bash
python3 controls/interactive_control.py
```

**Controls:**
- `W` or `↑` - Forward
- `S` or `↓` - Backward  
- `A` or `←` - Steer Left
- `D` or `→` - Steer Right
- `Space` - Stop Drive
- `C` - Center Steering
- `X` - All Off
- `Q` - Quit
- `H` - Help

**Example:**
```bash
# Just run it and start pressing keys!
python3 controls/interactive_control.py --host raspberrypi.local

# With service mode for faster response (if service is running):
python3 controls/interactive_control.py --host raspberrypi.local --service
```

### Option 2: Simple Command Line
Type commands and press Enter - easier if key detection doesn't work

```bash
python3 controls/simple_interactive.py
```

**Usage:**
```bash
RC Car> w      # Forward
RC Car> s      # Backward
RC Car> a      # Left
RC Car> d      # Right
RC Car> stop   # Stop
RC Car> c      # Center
RC Car> x      # All off
RC Car> quit   # Exit
```

## Setup (One Time)

### 1. On Raspberry Pi:
```bash
# Install dependencies
pip3 install pyserial

# Create directory
mkdir -p ~/rc_car_control

# Copy controller script to Pi (from your laptop)
scp controls/arduino_wasd_controller.py pi@raspberrypi.local:~/rc_car_control/
```

### 2. Test Connection:
```bash
# On Raspberry Pi, test locally first
python3 ~/rc_car_control/arduino_wasd_controller.py --list-ports
python3 ~/rc_car_control/arduino_wasd_controller.py -p /dev/ttyACM0 w
```

### 3. From Your Laptop:
```bash
# Run interactive control
python3 controls/interactive_control.py --host raspberrypi.local
```

## Optional: Faster Response with Service

For even faster response times, run a service on the Pi:

### On Raspberry Pi:
```bash
# Start service in background
python3 ~/rc_car_control/rc_car_service.py --mode file --port /dev/ttyACM0 &
```

### From Your Laptop:
```bash
# Use service mode
python3 controls/interactive_control.py --host raspberrypi.local --service
```

## Troubleshooting

**"Permission denied" on SSH:**
- Set up SSH keys: `ssh-copy-id pi@raspberrypi.local`

**Can't find Arduino:**
- Check port: `python3 arduino_wasd_controller.py --list-ports`
- Try different ports: `/dev/ttyACM0`, `/dev/ttyUSB0`

**Arrow keys don't work:**
- Use the simple interactive version: `python3 controls/simple_interactive.py`
- Or use W/A/S/D keys instead

**Slow response:**
- Use service mode: `--service` flag
- Or run service on Pi for faster file-based communication

## That's It!

Just run the interactive script and start controlling your RC car in real-time! 🚗

