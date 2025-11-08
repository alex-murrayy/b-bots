# Run on Raspberry Pi via SSH - Step by Step

## Prerequisites

1. **Arduino sketch uploaded** (from your laptop)
2. **Arduino connected to Raspberry Pi** via USB
3. **SSH access to Raspberry Pi**

## Step 1: Upload Sketch (On Your Laptop)

1. Open Arduino IDE
2. Open `controls/arduinoControls.ino`
3. **IMPORTANT:** Make sure `while(!Serial)` is commented out:
   ```cpp
   Serial.begin(115200);
   // while (!Serial) { ; }  // ← This line should be commented out!
   delay(500);
   Serial.println(F("WASD + Test Mode Ready"));
   ```
4. Select board: **Arduino Uno R4 WiFi** (or your board)
5. Select port: Your Arduino port
6. Click **Upload**
7. Wait for "Done uploading"
8. **Open Serial Monitor** (115200 baud)
9. **Verify you see:** "WASD + Test Mode Ready"
10. **Type 'w' and press Enter**
11. **You should see:** "FWD"
12. **Close Serial Monitor** (IMPORTANT!)

## Step 2: Copy Files to Raspberry Pi

**From your laptop:**

```bash
# Copy updated files to Pi
scp controls/arduino_wasd_controller.py pi@raspberrypi.local:~/b-bots/controls/
scp controls/verify_sketch.py pi@raspberrypi.local:~/b-bots/controls/
scp controls/test_communication.py pi@raspberrypi.local:~/b-bots/controls/
scp controls/debug_serial.py pi@raspberrypi.local:~/b-bots/controls/
scp controls/test_arduino.py pi@raspberrypi.local:~/b-bots/controls/
scp controls/interactive_control.py pi@raspberrypi.local:~/b-bots/controls/
```

**Or copy entire controls directory:**

```bash
scp -r controls/ pi@raspberrypi.local:~/b-bots/
```

## Step 3: SSH into Raspberry Pi

```bash
ssh pi@raspberrypi.local
cd ~/b-bots
```

## Step 4: Verify Arduino Sketch is Running

```bash
python3 controls/verify_sketch.py
```

**Expected output:**

```
✓ Startup message found - Sketch is running!
✓ Command response received - Communication working!
```

**If you see:**

```
✗ No startup messages received
```

**Then:**

1. Make sure Serial Monitor in Arduino IDE is closed
2. Re-upload the sketch
3. Verify sketch has `while(!Serial)` commented out
4. Try again

## Step 5: Test Communication

```bash
python3 controls/test_communication.py
```

**Expected output:**

```
✓ ALL TESTS PASSED - Arduino is working correctly!
```

**This tests:**

- Startup messages
- All commands (w, s, a, d, space, c, x)
- Command responses
- Communication timing

## Step 6: Run Interactive Control

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

## Troubleshooting

### Issue: "No startup messages"

**Solution:**

1. Close Arduino IDE Serial Monitor
2. Check sketch has `while(!Serial)` commented out
3. Re-upload sketch
4. Verify in Serial Monitor that startup messages appear
5. Close Serial Monitor
6. Try Python script again

### Issue: "Permission denied"

**Solution:**

```bash
sudo usermod -a -G dialout $USER
# Log out and back in, or:
newgrp dialout
```

### Issue: "Port not found"

**Solution:**

```bash
# List ports
python3 controls/arduino_wasd_controller.py --list-ports

# Try different port
python3 controls/verify_sketch.py --port /dev/ttyUSB0
```

### Issue: "Commands sent but no response"

**Check:**

1. Is Serial Monitor closed?
2. Does Serial Monitor show responses when you send commands manually?
3. If yes → Python timing issue (should be fixed now)
4. If no → Sketch issue, re-upload

## Quick Test Sequence

```bash
# 1. Verify sketch
python3 controls/verify_sketch.py

# 2. Test communication
python3 controls/test_communication.py

# 3. Test single command
python3 controls/arduino_wasd_controller.py --port /dev/ttyACM0 --debug w

# 4. Run interactive control
python3 controls/interactive_control.py
```

## Monitoring Serial Communication

**Terminal 1:**

```bash
python3 controls/debug_serial.py --port /dev/ttyACM0
```

**Terminal 2 (new SSH session):**

```bash
python3 controls/arduino_wasd_controller.py --port /dev/ttyACM0 --debug w
```

**You should see in Terminal 1:**

- Startup messages
- "FWD" response when command is sent

## Expected Results

### ✅ Working:

- Startup messages: "WASD + Test Mode Ready"
- Command responses: "FWD", "REV", "LEFT TAP", etc.
- Motors respond to commands
- LED flashes (if connected)

### ❌ Not Working:

- No startup messages → Sketch not running
- No command responses → Check Serial Monitor, verify sketch
- No motor movement → Check wiring, verify pins

## Important Notes

1. **Only one program can use serial at a time**

   - Close Serial Monitor before using Python
   - Close Python scripts before using Serial Monitor

2. **Arduino resets on serial connection**

   - This is normal
   - Code waits 2-3 seconds for initialization

3. **`while(!Serial)` blocks Python**
   - Must be commented out in sketch
   - Only use during development with Serial Monitor

## Next Steps

Once everything works:

1. **Test all commands**
2. **Verify motors work**
3. **Run interactive control**
4. **Integrate with delivery system**
