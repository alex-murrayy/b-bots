# RC Car Controls System

Complete control system for RC car with Arduino-based motor control using WASD protocol.

## Quick Start

### 1. Setup Arduino

- Upload `arduinoControls.ino` to your Arduino
- Connect Arduino to Raspberry Pi via USB
- Find port: `python3 controls/arduino_wasd_controller.py --list-ports`

### 2. Test Connection

```bash
python3 controls/test_arduino.py
```

### 3. Run Interactive Control

```bash
# Interactive control (recommended)
python3 controls/interactive_control.py

# Simple command-line control
python3 controls/simple_interactive.py

# With monitoring/benchmarking
python3 controls/interactive_control.py --monitor
```

**Controls:**

- `W` - Forward
- `S` - Backward
- `A` - Steer Left
- `D` - Steer Right
- `Space` - Stop Drive
- `C` - Center Steering
- `X` - All Off
- `Q` - Quit

See `QUICK_START.md` for detailed setup instructions.

## System Overview

### Hardware

- **Arduino Uno R4** (or compatible) with `arduinoControls.ino` sketch
- **Motor Driver** (L298N, TB6612FNG, DRV8833, or compatible)
- **Drive Motor** (forward/reverse)
- **Steering Motor/Servo** (left/right)

### Software Components

1. **Arduino Sketch** (`arduinoControls.ino`)

   - WASD protocol (single character commands)
   - 115200 baud serial communication
   - Latched drive, momentary steering
   - Test mode (press 't' to enter)

2. **Python Controllers**

   - `arduino_wasd_controller.py` - Low-level controller class
   - `interactive_control.py` - Real-time keyboard control
   - `continuous_control.py` - Press-and-hold control
   - `simple_interactive.py` - Simple command-line interface

3. **Remote Control**

   - `rc_car_service.py` - Background service on Raspberry Pi
   - `rc_car_client.py` - Client for remote control via SSH

4. **Monitoring**
   - `motor_monitor.py` - Performance monitoring and benchmarking

## Controls

### Command Protocol (WASD)

| Command     | Description     | Arduino Behavior                 |
| ----------- | --------------- | -------------------------------- |
| `w`         | Forward         | Latched (stays on until stopped) |
| `s`         | Backward        | Latched (stays on until stopped) |
| `a`         | Steer Left      | Momentary tap (200ms pulse)      |
| `d`         | Steer Right     | Momentary tap (200ms pulse)      |
| ` ` (space) | Stop Drive      | Stops forward/backward           |
| `c`         | Center Steering | Centers steering                 |
| `x`         | All Off         | Stops everything                 |
| `t`         | Test Mode       | Enter test mode on Arduino       |

### Interactive Control

**Keyboard Controls:**

- `W` - Forward (release to auto-stop if keyboard library installed)
- `S` - Backward (release to auto-stop if keyboard library installed)
- `A` - Steer Left
- `D` - Steer Right
- `Space` - Stop Drive
- `C` - Center Steering
- `X` - All Off
- `Q` - Quit
- `H` - Help

## Usage

### Local Control

```bash
# Interactive control (best experience)
python3 controls/interactive_control.py

# Simple command-line
python3 controls/simple_interactive.py

# Continuous control (press and hold)
python3 controls/continuous_control.py
```

### Remote Control (via Raspberry Pi)

```bash
# Interactive control via SSH
python3 controls/interactive_control.py --host raspberrypi.local

# With service mode (faster)
python3 controls/interactive_control.py --host raspberrypi.local --service

# Simple command-line
python3 controls/simple_interactive.py --host raspberrypi.local
```

### Monitoring and Benchmarking

```bash
# Run with monitoring
python3 controls/interactive_control.py --monitor

# View real-time stats
# Stats are printed automatically during control session
```

## Arduino Setup

### Upload Sketch

1. Open `arduinoControls.ino` in Arduino IDE
2. Select your Arduino board (Arduino Uno R4)
3. Select the correct port
4. Upload the sketch

### Pin Configuration

Edit `arduinoControls.ino` to match your wiring:

```cpp
const int PIN_FWD   = 5;  // Forward pin
const int PIN_REV   = 7;  // Reverse pin
const int PIN_LEFT  = 8;  // Left steering pin
const int PIN_RIGHT = 6;  // Right steering pin
```

### Configuration Options

```cpp
bool ACTIVE_LOW = false;          // Set true if ON = LOW
bool USE_BRAKE_BEFORE_REV = false; // Set true if reverse needs brake
int steerPulse = 200;             // Steering pulse duration (ms)
```

## Raspberry Pi Setup

### 1. Install Dependencies

```bash
# On Raspberry Pi
pip3 install pyserial
```

### 2. Copy Files to Raspberry Pi

From your laptop, copy the controller script to your Raspberry Pi:

```bash
# Create directory
ssh pi@raspberrypi.local "mkdir -p ~/rc_car_control"

# Copy files
scp controls/arduino_wasd_controller.py pi@raspberrypi.local:~/rc_car_control/
scp controls/rc_car_service.py pi@raspberrypi.local:~/rc_car_control/
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

### 5. Remote Control Methods

**Method 1: Direct SSH Command Execution**

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
```

**Method 2: Background Service (Recommended)**

Set up a background service on the Raspberry Pi:

```bash
# On Raspberry Pi: Start the service
python3 ~/rc_car_control/rc_car_service.py --mode file --port /dev/ttyACM0 &

# From laptop: Send commands via file
ssh pi@raspberrypi.local "echo 'w' > /tmp/rc_car_command"
ssh pi@raspberrypi.local "echo 's' > /tmp/rc_car_command"
ssh pi@raspberrypi.local "echo 'a' > /tmp/rc_car_command"
ssh pi@raspberrypi.local "echo 'd' > /tmp/rc_car_command"
ssh pi@raspberrypi.local "echo 'space' > /tmp/rc_car_command"
```

**Method 3: Systemd Service (Auto-start)**

Create a systemd service for automatic startup:

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

## Monitoring and Benchmarking

The `motor_monitor.py` module tracks:

- Command execution timing
- Drive time (forward/backward)
- Turn counts (left/right)
- Response times
- Error rates
- Session statistics

### Example Output

```
╔══════════════════════════════════════════════════════════════╗
║              Motor Control Session Summary                    ║
╠══════════════════════════════════════════════════════════════╣
║  Session Duration:          120.5 seconds                    ║
║  Total Commands:               45                            ║
║  Commands/Second:            0.37                            ║
║  Average Response:           45.2 ms                         ║
║  Errors:                       0                             ║
╠══════════════════════════════════════════════════════════════╣
║  Commands by Type:                                           ║
║    Forward:                   12                             ║
║    Backward:                   3                             ║
║    Left Turns:                15                             ║
║    Right Turns:               12                             ║
║    Stop:                       8                             ║
╠══════════════════════════════════════════════════════════════╣
║  Drive Time:                                                 ║
║    Forward:           45.3 seconds                           ║
║    Backward:           8.2 seconds                           ║
╚══════════════════════════════════════════════════════════════╝
```

## Troubleshooting

### Car Doesn't Stop When Releasing 'W'

**Solution:** Install the `keyboard` library for proper key release detection:

```bash
pip3 install keyboard
```

Or manually press `Space` to stop the car.

### Right Turn Doesn't Work

**Solution:** This has been fixed. Ensure you're using the latest code:

- `arduino_wasd_controller.py` sends lowercase 'd' command
- `arduinoControls.ino` accepts both 'd' and 'D' (case-insensitive)

### Serial Port Not Found

**Solution:** List available ports:

```bash
python3 controls/arduino_wasd_controller.py --list-ports
```

Common ports:

- Linux/Mac: `/dev/ttyACM0`, `/dev/ttyUSB0`
- Windows: `COM3`, `COM4`, etc.

### Permission Denied (Serial Port)

**Solution:** Add user to dialout group:

```bash
sudo usermod -a -G dialout $USER
# Log out and log back in
```

### Slow Response (Remote Control)

**Solution:** Use service mode for faster response:

```bash
# On Pi: Start service
python3 ~/rc_car_control/rc_car_service.py --mode file &

# From laptop: Use service mode
python3 controls/interactive_control.py --host raspberrypi.local --service
```

### SSH Connection Issues

**Solution:**

- Ensure SSH is enabled on Raspberry Pi: `sudo systemctl enable ssh`
- Check network connectivity: `ping raspberrypi.local`
- Use IP address instead of hostname if DNS doesn't work
- Set up SSH keys: `ssh-copy-id pi@raspberrypi.local`

## File Structure

```
controls/
├── arduinoControls.ino          # Arduino sketch (WASD protocol)
├── arduino_wasd_controller.py   # Main controller class
├── interactive_control.py       # Real-time interactive control
├── continuous_control.py        # Press-and-hold control
├── simple_interactive.py        # Simple CLI control
├── rc_car_service.py            # Background service
├── rc_car_client.py             # Remote client
├── motor_monitor.py             # Monitoring/benchmarking
├── quick_control.sh             # Quick control script
├── setup_pi.sh                  # Pi setup script
└── README.md                    # This file
```

## Protocol Details

### Arduino Communication

- **Baud Rate**: 115200
- **Protocol**: Single character commands
- **Case**: Case-insensitive (accepts both 'w' and 'W')
- **Drive**: Latched (remains active until stopped)
- **Steering**: Momentary (200ms pulse, auto-centers)

### Command Flow

```
User Input → Python Controller → Serial (115200 baud) → Arduino → Motors
```

### Response Handling

Arduino sends responses via Serial.println():

- `"FWD"` - Forward engaged
- `"REV"` - Reverse engaged
- `"LEFT TAP"` - Left turn executed
- `"RIGHT TAP"` - Right turn executed
- `"NEUTRAL DRIVE"` - Drive stopped
- `"CENTER"` - Steering centered
- `"ALL OFF"` - Everything stopped

## Safety Notes

- Always test with low speeds first
- Ensure adequate power supply for motors
- Use appropriate fuses for overcurrent protection
- Keep hands clear of moving parts during operation
- The system includes auto-stop safety features

## License

This code is provided as-is for educational and development purposes.
