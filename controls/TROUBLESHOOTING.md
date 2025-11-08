# Troubleshooting Guide - Arduino Not Responding

## Problem: LED Not Flashing / No Response

If the Arduino LED is **NOT flashing** when you send commands, this indicates the Arduino is **not receiving or processing commands**.

## Quick Diagnostic Steps

### Step 1: Verify Sketch is Uploaded and Running

```bash
# Run verification script
python3 controls/verify_sketch.py

# This will check:
# - Startup messages from Arduino
# - Command responses
# - Communication status
```

**Expected output:**
```
✓ Startup message found - Sketch is running!
✓ Command response received - Communication working!
```

**If you see:**
```
✗ No startup messages received
✗ No response received
```

**Then the sketch is likely not running!**

### Step 2: Check Arduino Serial Monitor

1. **Open Arduino IDE**
2. **Select your Arduino board** (Tools -> Board -> Arduino Uno R4 WiFi)
3. **Select the port** (Tools -> Port -> /dev/ttyACM0)
4. **Open Serial Monitor** (Tools -> Serial Monitor)
5. **Set baud rate to 9600** (bottom right of Serial Monitor)
6. **Check for messages:**
   - Should see: "WASD + Test Mode Ready"
   - Should see help text

**If you see nothing:**
- Sketch is not uploaded
- Sketch is not running
- Wrong baud rate
- Arduino is in wrong mode

### Step 3: Re-upload Sketch

1. **Open `arduinoControls.ino` in Arduino IDE**
2. **Verify board and port are correct**
3. **Click Upload** (arrow icon)
4. **Wait for "Done uploading" message**
5. **Open Serial Monitor** and verify you see startup messages

### Step 4: Test Manually in Serial Monitor

1. **Open Serial Monitor** (9600 baud)
2. **Type 'w' and press Enter**
3. **You should see:**
   - Arduino sends: "FWD"
   - LED should flash (if you have an LED on pin 13)
   - Motors should move (if connected)

**If nothing happens:**
- Sketch is not processing commands
- Check wiring connections
- Verify pin numbers in sketch match your hardware

### Step 5: Check Arduino Hardware

**Verify Arduino is working:**
1. **Upload a simple test sketch:**
   ```cpp
   void setup() {
     Serial.begin(9600);
     pinMode(13, OUTPUT);
   }
   
   void loop() {
     Serial.println("Hello");
     digitalWrite(13, HIGH);
     delay(1000);
     digitalWrite(13, LOW);
     delay(1000);
   }
   ```
2. **If this works:** Original sketch has an issue
3. **If this doesn't work:** Arduino hardware issue

## Common Issues and Solutions

### Issue 1: No Startup Messages

**Symptoms:**
- `verify_sketch.py` shows no startup messages
- Serial Monitor shows nothing
- No responses to commands

**Solutions:**
1. **Re-upload the sketch**
2. **Check baud rate matches** (should be 9600)
3. **Check Serial.begin(9600) is in setup()**
4. **Verify sketch compiles without errors**

### Issue 2: Commands Sent But No Response

**Symptoms:**
- Python shows "Command sent"
- No LED flashing
- No motor movement
- No Serial responses

**Solutions:**
1. **Check Arduino Serial Monitor** - see if commands arrive
2. **Verify sketch has command handlers** (switch statement in loop())
3. **Check pin numbers** - verify pins match your wiring
4. **Test in Serial Monitor** - send commands manually

### Issue 3: Wrong Baud Rate

**Symptoms:**
- Garbled text in Serial Monitor
- No communication
- Timeout errors

**Solutions:**
1. **Verify baud rate in sketch:** `Serial.begin(9600);`
2. **Set Serial Monitor to 9600**
3. **Use same baud rate in Python:** `baudrate=9600`

### Issue 4: Arduino Resets on Connection

**Symptoms:**
- Arduino resets when Python connects
- Connection works but unstable
- Random resets

**Solutions:**
1. **This is normal** - Arduino resets on serial connection
2. **Wait 2 seconds after connection** (code does this)
3. **Don't connect multiple programs** to same port

### Issue 5: Permission Denied

**Symptoms:**
- "Permission denied" error
- Cannot open /dev/ttyACM0

**Solutions:**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in, or:
newgrp dialout

# Verify:
groups
# Should show 'dialout'
```

## Diagnostic Commands

### Check Arduino Communication

```bash
# Verify sketch is running
python3 controls/verify_sketch.py

# Check Arduino connection
python3 controls/check_arduino.py

# Test with debug output
python3 controls/test_arduino.py --debug
```

### Check Serial Port

```bash
# List ports
python3 controls/arduino_wasd_controller.py --list-ports

# Check if device exists
ls -l /dev/ttyACM*

# Check USB devices
dmesg | grep -i usb | tail -10
```

### Monitor Serial Communication

```bash
# Monitor all serial data
python3 controls/debug_serial.py --port /dev/ttyACM0

# In another terminal, send commands:
python3 controls/arduino_wasd_controller.py --port /dev/ttyACM0 w
```

## Step-by-Step Debugging Workflow

### Workflow 1: Verify Sketch is Running

```bash
# 1. Run verification
python3 controls/verify_sketch.py

# 2. If no startup messages:
#    - Open Arduino IDE
#    - Re-upload sketch
#    - Check Serial Monitor
#    - Verify baud rate

# 3. If startup messages but no responses:
#    - Check command handlers in sketch
#    - Test commands manually in Serial Monitor
#    - Verify pin connections
```

### Workflow 2: Test Arduino Hardware

```bash
# 1. Upload simple test sketch (see above)
# 2. Open Serial Monitor
# 3. Should see "Hello" every second
# 4. LED on pin 13 should blink
# 5. If this works, original sketch has issue
# 6. If this doesn't work, Arduino hardware issue
```

### Workflow 3: Test Communication

```bash
# Terminal 1: Monitor serial
python3 controls/debug_serial.py --port /dev/ttyACM0

# Terminal 2: Send commands
python3 controls/arduino_wasd_controller.py --port /dev/ttyACM0 --debug w

# Check if:
# - Commands appear in monitor
# - Responses appear in monitor
# - Timing is correct
```

## Expected Behavior

### ✅ Working Correctly:

1. **Startup:**
   - Arduino sends "WASD + Test Mode Ready"
   - Help text appears
   - Serial Monitor shows messages

2. **Commands:**
   - Sending 'w' → Arduino responds "FWD"
   - Sending 's' → Arduino responds "REV"
   - Sending 'a' → Arduino responds "LEFT TAP"
   - LED flashes (if connected to pin 13)
   - Motors move (if connected)

3. **Python:**
   - Connection successful
   - Commands sent successfully
   - Responses received

### ⚠️ Issues:

1. **No startup messages:**
   - Sketch not uploaded
   - Sketch not running
   - Wrong baud rate

2. **No command responses:**
   - Commands not processed
   - Serial.println() missing
   - Timing issues

3. **No LED flashing:**
   - Commands not received
   - Sketch not processing
   - Hardware issue

## Quick Fixes

### Fix 1: Re-upload Sketch

```bash
# 1. Open Arduino IDE
# 2. Open arduinoControls.ino
# 3. Select board: Arduino Uno R4 WiFi
# 4. Select port: /dev/ttyACM0
# 5. Click Upload
# 6. Wait for "Done uploading"
# 7. Open Serial Monitor (9600 baud)
# 8. Verify startup messages
```

### Fix 2: Check Baud Rate

```python
# In arduinoControls.ino, verify:
Serial.begin(9600);  // Must be 9600

# In Python, verify:
baudrate=9600  # Must match
```

### Fix 3: Test in Serial Monitor

1. Open Arduino IDE Serial Monitor
2. Set baud rate to 9600
3. Type 'w' and press Enter
4. Should see "FWD" response
5. If you see this, communication works
6. If not, sketch issue

## Getting Help

If still having issues:

1. **Run verification:**
   ```bash
   python3 controls/verify_sketch.py > verify.log 2>&1
   ```

2. **Check Serial Monitor output:**
   - Copy all messages
   - Note any errors

3. **Check Arduino IDE:**
   - Verify sketch compiles
   - Check for errors
   - Verify upload successful

4. **Share information:**
   - Output of `verify_sketch.py`
   - Serial Monitor output
   - Arduino IDE messages
   - Error messages

## Next Steps

Once Arduino is responding:

1. **Test all commands:**
   ```bash
   python3 controls/test_arduino.py --debug
   ```

2. **Run interactive control:**
   ```bash
   python3 controls/interactive_control.py
   ```

3. **Verify motors work:**
   - Send commands
   - Check motor movement
   - Verify steering works

