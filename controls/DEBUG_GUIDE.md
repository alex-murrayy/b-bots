# Debugging Guide - Running on Raspberry Pi via SSH

## Quick Start: SSH and Debug

### 1. SSH into Raspberry Pi

```bash
ssh pi@raspberrypi.local
# Or use IP address:
ssh pi@192.168.1.XXX
```

### 2. Navigate to Project Directory

```bash
cd ~/b-bots
# Or wherever your project is located
```

### 3. **FIRST: Verify Arduino Sketch is Running**

```bash
# CRITICAL: Check if Arduino sketch is actually running
python3 controls/verify_sketch.py

# This will tell you if:
# - Sketch is uploaded and running
# - Arduino is sending startup messages
# - Commands are being processed
```

**If this shows no startup messages → Arduino sketch is NOT running!**
- Open Arduino IDE
- Re-upload the sketch
- Check Serial Monitor

### 4. Run Debug Test

```bash
# Basic test with debugging
python3 controls/test_arduino.py --debug

# Comprehensive test suite
python3 controls/test_arduino_debug.py --debug

# Check Arduino communication
python3 controls/check_arduino.py
```

## Step-by-Step Debugging Workflow

### Step 1: Verify Arduino Connection

```bash
# List available serial ports
python3 controls/arduino_wasd_controller.py --list-ports

# Expected output:
# Available serial ports:
#   /dev/ttyACM0 - Arduino Uno
```

### Step 2: Test Basic Connection

```bash
# Test connection with debug output
python3 controls/test_arduino.py --port /dev/ttyACM0 --debug
```

**What to look for:**

- ✅ "Connected to Arduino" message
- ✅ Arduino startup message (if any)
- ✅ Commands being sent
- ⚠️ Responses (may be None - that's OK if Arduino LED flashes)

### Step 3: Monitor Serial Communication

**Terminal 1 (SSH): Monitor serial**

```bash
python3 controls/debug_serial.py --port /dev/ttyACM0
```

**Terminal 2 (SSH): Send commands**

```bash
python3 controls/arduino_wasd_controller.py --port /dev/ttyACM0 w
python3 controls/arduino_wasd_controller.py --port /dev/ttyACM0 s
python3 controls/arduino_wasd_controller.py --port /dev/ttyACM0 a
```

This will show you exactly what the Arduino is sending back.

### Step 4: Test Interactive Control

```bash
# Run interactive control with debugging
python3 controls/interactive_control.py --arduino-port /dev/ttyACM0
```

## Common Issues and Solutions

### Issue 1: "Permission denied" Error

**Solution:**

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Log out and log back in, or:
newgrp dialout

# Verify:
groups
# Should show 'dialout' in the list
```

### Issue 2: Port Not Found

**Check:**

```bash
# List ports
python3 controls/arduino_wasd_controller.py --list-ports

# Check if device exists
ls -l /dev/ttyACM* /dev/ttyUSB*

# Check dmesg for USB devices
dmesg | tail -20
```

**Solutions:**

- Try different port: `/dev/ttyUSB0`, `/dev/ttyACM1`
- Reconnect Arduino USB cable
- Check USB cable is data-capable (not charge-only)

### Issue 3: No Response from Arduino

**This is OK if:**

- ✅ Arduino LED flashes when commands are sent
- ✅ Motors respond to commands
- ✅ Arduino sketch is uploaded correctly

**Arduino may not send responses if:**

- Serial.println() is commented out
- Responses are sent but timing is off
- Buffer issues

**Debug:**

```bash
# Use serial monitor to see what Arduino sends
python3 controls/debug_serial.py --port /dev/ttyACM0

# In another terminal, send commands:
python3 controls/arduino_wasd_controller.py --port /dev/ttyACM0 --debug w
```

### Issue 4: Commands Not Executing

**Check Arduino Sketch:**

1. Verify sketch is uploaded: Check Arduino IDE
2. Check Serial Monitor in Arduino IDE to see if commands are received
3. Verify baud rate matches (9600)

**Test Arduino directly:**

```bash
# Send command and check Arduino response
python3 controls/arduino_wasd_controller.py --port /dev/ttyACM0 --debug w

# Expected: Arduino LED should flash, motors should move
```

### Issue 5: Interactive Control Not Working

**Try simple mode:**

```bash
# Use simple interactive (type commands)
python3 controls/simple_interactive.py --arduino-port /dev/ttyACM0
```

**Check terminal:**

- Make sure you're in a real terminal (not non-interactive SSH)
- Try: `echo $TERM` (should show something like `xterm-256color`)

## Debugging Tools

### 1. Basic Test (`test_arduino.py`)

```bash
# Quick test
python3 controls/test_arduino.py

# With debugging
python3 controls/test_arduino.py --debug

# Different port
python3 controls/test_arduino.py --port /dev/ttyUSB0 --debug
```

### 2. Comprehensive Test (`test_arduino_debug.py`)

```bash
# Run all tests
python3 controls/test_arduino_debug.py --debug

# Run specific test
python3 controls/test_arduino_debug.py --test connection --debug
python3 controls/test_arduino_debug.py --test communication --debug
python3 controls/test_arduino_debug.py --test commands --debug
python3 controls/test_arduino_debug.py --test timing --debug
python3 controls/test_arduino_debug.py --test raw --debug
```

### 3. Serial Monitor (`debug_serial.py`)

```bash
# Monitor all serial communication
python3 controls/debug_serial.py --port /dev/ttyACM0

# This will show:
# - Arduino startup messages
# - All responses from Arduino
# - Real-time communication
```

### 4. Interactive Controller with Debug

```bash
# Run interactive control
python3 controls/interactive_control.py --arduino-port /dev/ttyACM0

# Note: Debug output is disabled by default to avoid clutter
# If you need debug, modify the code or use test scripts
```

## SSH-Specific Tips

### 1. Keep SSH Session Alive

```bash
# In your ~/.ssh/config (on your laptop):
Host raspberrypi
    HostName raspberrypi.local
    User pi
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

### 2. Run in Background (for testing)

```bash
# Run test in background
nohup python3 controls/test_arduino.py --debug > test.log 2>&1 &

# Check output
tail -f test.log
```

### 3. Multiple SSH Sessions

```bash
# Terminal 1: Monitor serial
ssh pi@raspberrypi.local
python3 controls/debug_serial.py

# Terminal 2: Send commands
ssh pi@raspberrypi.local
python3 controls/arduino_wasd_controller.py w

# Terminal 3: Run interactive control
ssh pi@raspberrypi.local
python3 controls/interactive_control.py
```

### 4. Copy Files to Pi

```bash
# From your laptop:
scp controls/test_arduino.py pi@raspberrypi.local:~/b-bots/controls/
scp controls/arduino_wasd_controller.py pi@raspberrypi.local:~/b-bots/controls/
```

## Complete Debugging Workflow

### Workflow 1: First Time Setup

```bash
# 1. SSH into Pi
ssh pi@raspberrypi.local

# 2. Navigate to project
cd ~/b-bots

# 3. Check Arduino port
python3 controls/arduino_wasd_controller.py --list-ports

# 4. Test connection
python3 controls/test_arduino.py --debug

# 5. If successful, run interactive control
python3 controls/interactive_control.py
```

### Workflow 2: Troubleshooting No Response

```bash
# 1. Check Arduino is receiving commands
python3 controls/debug_serial.py --port /dev/ttyACM0

# 2. In another terminal, send test command
python3 controls/arduino_wasd_controller.py --port /dev/ttyACM0 --debug w

# 3. Check if Arduino LED flashes (indicates command received)

# 4. Check Arduino Serial Monitor (in Arduino IDE) for responses

# 5. Verify Arduino sketch has Serial.println() statements
```

### Workflow 3: Testing All Commands

```bash
# Run comprehensive test
python3 controls/test_arduino_debug.py --debug

# This will test:
# - Connection
# - Serial communication
# - All commands (w, s, a, d, space, c, x)
# - Response timing
# - Raw serial communication
```

## Expected Behavior

### ✅ Working Correctly:

1. **Connection:**

   - "Connected to Arduino" message
   - No errors

2. **Commands:**

   - Arduino LED flashes when command sent
   - Motors respond (if connected)
   - No Python errors

3. **Responses:**
   - May be `None` (OK if Arduino executes command)
   - Or Arduino response like "FWD", "REV", etc.

### ⚠️ Issues to Investigate:

1. **No connection:**

   - Check port, permissions, USB cable

2. **Commands not executing:**

   - Check Arduino sketch is uploaded
   - Check baud rate matches
   - Check Serial Monitor in Arduino IDE

3. **Responses always None:**
   - Check Arduino sketch has Serial.println()
   - Use debug_serial.py to monitor
   - Check timing (responses may arrive after timeout)

## Quick Reference

```bash
# List ports
python3 controls/arduino_wasd_controller.py --list-ports

# Test connection
python3 controls/test_arduino.py --debug

# Comprehensive test
python3 controls/test_arduino_debug.py --debug

# Monitor serial
python3 controls/debug_serial.py --port /dev/ttyACM0

# Interactive control
python3 controls/interactive_control.py --arduino-port /dev/ttyACM0

# Simple mode
python3 controls/simple_interactive.py --arduino-port /dev/ttyACM0

# Send single command
python3 controls/arduino_wasd_controller.py --port /dev/ttyACM0 --debug w
```

## Next Steps

1. **If everything works:**

   - Run interactive control: `python3 controls/interactive_control.py`
   - Test all commands
   - Integrate with delivery system

2. **If issues persist:**
   - Check Arduino Serial Monitor
   - Verify Arduino sketch is correct
   - Check wiring connections
   - Review error messages carefully

## Getting Help

If you're stuck:

1. Run `test_arduino_debug.py --debug` and share output
2. Check Arduino Serial Monitor output
3. Verify Arduino sketch is uploaded correctly
4. Check permissions: `groups` (should include 'dialout')
5. Check port: `ls -l /dev/ttyACM*`
