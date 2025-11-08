# Quick Debug Guide - Run This Now on Pi

## Immediate Steps to Debug

### Step 1: Upload Updated Sketch (On Your Laptop)

1. **Open Arduino IDE**
2. **Open `arduinoControls.ino`**
3. **Verify the sketch has this in setup():**
   ```cpp
   Serial.begin(9600);
   while (!Serial) {
     ; // Wait for serial port to connect
   }
   delay(500);
   Serial.println(F("WASD + Test Mode Ready"));
   ```
4. **Upload the sketch**
5. **Open Serial Monitor (9600 baud)**
6. **Verify you see:** "WASD + Test Mode Ready"
7. **Type 'w' and press Enter**
8. **You should see:** "FWD"
9. **Close Serial Monitor** (IMPORTANT - only one program can use serial)

### Step 2: SSH into Raspberry Pi

```bash
ssh pi@raspberrypi.local
cd ~/b-bots
```

### Step 3: Run Verification Script

```bash
python3 controls/verify_sketch.py
```

**What to look for:**
- ✅ "Startup message found" → Sketch is running
- ✅ "Command response received" → Communication works
- ❌ "No startup messages" → Sketch not running, re-upload

### Step 4: Test Communication

```bash
python3 controls/test_communication.py
```

This will test all commands and show exactly what's happening.

### Step 5: If Still Not Working

**Check if Serial Monitor is closed:**
- Make sure Arduino IDE Serial Monitor is closed
- Only one program can use serial at a time

**Monitor serial in real-time:**
```bash
# Terminal 1
python3 controls/debug_serial.py

# Terminal 2 (new SSH session)
python3 controls/arduino_wasd_controller.py --debug w
```

## Quick Test Sequence

```bash
# 1. Verify sketch
python3 controls/verify_sketch.py

# 2. Test communication
python3 controls/test_communication.py

# 3. Test single command
python3 controls/arduino_wasd_controller.py --port /dev/ttyACM0 --debug w

# 4. If all work, run interactive control
python3 controls/interactive_control.py
```

## What Each Script Does

- **`verify_sketch.py`** - Checks if Arduino sketch is running and sending messages
- **`test_communication.py`** - Tests all commands and shows responses
- **`debug_serial.py`** - Monitors all serial communication in real-time
- **`test_arduino.py`** - Basic test with debugging

## Expected Results

### ✅ Working:
- Startup messages received
- Command responses received ("FWD", "REV", etc.)
- Motors respond (if connected)

### ❌ Not Working:
- No startup messages → Re-upload sketch
- No command responses → Check Serial Monitor, verify sketch
- No motor movement → Check wiring, verify pins

## Most Common Issue

**Serial Monitor is open in Arduino IDE**
- Close Serial Monitor
- Wait 5 seconds
- Try Python script again

## Next Steps

Once verification works:
1. Run: `python3 controls/test_communication.py`
2. If successful: `python3 controls/interactive_control.py`
3. Test all commands
4. Verify motors work

