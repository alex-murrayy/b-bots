# Quick Start Guide - Running the RC Car Controls

## Prerequisites

1. **Arduino Setup**

   - Upload `arduinoControls.ino` to your Arduino
   - Connect Arduino to Raspberry Pi via USB
   - Note the port (usually `/dev/ttyACM0`)

2. **Python Dependencies**

   ```bash
   pip3 install pyserial
   ```

3. **Permissions** (if needed)
   ```bash
   sudo usermod -a -G dialout $USER
   # Log out and log back in for changes to take effect
   ```

## Step 1: Find Your Arduino Port

```bash
python3 controls/arduino_wasd_controller.py --list-ports
```

Common ports:

- `/dev/ttyACM0` (most common for Arduino Uno)
- `/dev/ttyUSB0` (if using USB-to-serial adapter)

## Step 2: Test Arduino Connection

```bash
# Test basic connection
python3 controls/test_arduino.py
```

This will test:

- Connection to Arduino
- Forward command
- Stop command
- Left/Right commands
- All Off command

## Step 3: Run Interactive Control

### Option A: Interactive Control (Recommended)

```bash
python3 controls/interactive_control.py
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
- `H` - Help

### Option B: Simple Interactive (Type Commands)

```bash
python3 controls/simple_interactive.py
```

**Usage:**

- Type commands and press Enter
- Commands: `w`, `s`, `a`, `d`, `stop`, `c`, `x`, `quit`

### Option C: With Monitoring

```bash
python3 controls/interactive_control.py --monitor
```

This will track:

- Command execution timing
- Drive time
- Turn counts
- Response times
- Session statistics

## Step 4: Specify Port (if needed)

If your Arduino is on a different port:

```bash
python3 controls/interactive_control.py --arduino-port /dev/ttyUSB0
```

## Troubleshooting

### "Permission denied" Error

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Log out and log back in, or:
newgrp dialout
```

### "Port not found" Error

```bash
# List available ports
python3 controls/arduino_wasd_controller.py --list-ports

# Check if Arduino is connected
ls -l /dev/ttyACM* /dev/ttyUSB*

# Try different port
python3 controls/interactive_control.py --arduino-port /dev/ttyUSB0
```

### "Could not connect" Error

1. Check Arduino is powered on
2. Check USB cable is connected
3. Verify port with `--list-ports`
4. Check permissions (see above)
5. Try uploading Arduino sketch again

### Script Exits Immediately

1. Make sure you're in a terminal (not SSH without TTY)
2. Try simple interactive mode: `python3 controls/simple_interactive.py`
3. Check for errors in output

## Examples

### Basic Usage

```bash
# Start interactive control
python3 controls/interactive_control.py

# Press keys to control:
# W - Forward
# S - Backward
# A - Left
# D - Right
# Space - Stop
# Q - Quit
```

### With Monitoring

```bash
# Start with monitoring enabled
python3 controls/interactive_control.py --monitor

# At the end, you'll see statistics:
# - Total commands
# - Drive time
# - Response times
# - Error counts
```

### Test Connection First

```bash
# Test Arduino connection
python3 controls/test_arduino.py

# If successful, run interactive control
python3 controls/interactive_control.py
```

## What to Expect

1. **Script starts**: Shows connection message
2. **Help menu**: Displays control instructions
3. **Ready**: "Waiting for input..." message
4. **Press keys**: Car responds to W/S/A/D
5. **Status updates**: Shows current action on screen
6. **Press Q**: Quits and stops car

## Tips

1. **Always stop before quitting**: Press Space, then Q
2. **Use Space to stop**: Drive commands are latched
3. **Test first**: Run `test_arduino.py` before interactive control
4. **Check permissions**: If connection fails, check dialout group
5. **Monitor mode**: Use `--monitor` to track performance

## Next Steps

Once controls are working:

1. Test all commands (forward, backward, left, right)
2. Test stop functionality
3. Try monitoring mode to see performance
4. Integrate with delivery system

## Need Help?

- Check `controls/README.md` for detailed documentation
- Check `controls/TROUBLESHOOTING.md` for common issues
- Check `controls/RUN_ON_PI.md` for SSH setup
- Run test script: `python3 controls/test_arduino.py --debug`
- Check Arduino serial monitor for debug output (115200 baud)
