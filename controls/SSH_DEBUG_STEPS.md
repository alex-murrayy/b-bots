# SSH Debugging Steps - Arduino Not Responding

## Problem: LED Not Flashing, No Responses

Your Arduino sketch **should** be sending responses, but Python isn't receiving them. Let's debug step by step.

## Step-by-Step Debugging on Raspberry Pi

### Step 1: Verify Sketch is Uploaded

**On your laptop (with Arduino IDE):**

1. Open Arduino IDE
2. Open `arduinoControls.ino`
3. Select board: **Arduino Uno R4 WiFi** (or your board)
4. Select port: Your Arduino port
5. Click **Upload**
6. Wait for "Done uploading"
7. **Open Serial Monitor** (Tools -> Serial Monitor)
8. **Set baud rate to 9600**
9. **You should see:**
   ```
   WASD + Test Mode Ready
   Normal: W=Fwd  S=Rev  A=LeftTap  D=RightTap  Space=stop  C=center  X=all stop
   ...
   ```

**If you don't see this → Sketch is NOT uploaded correctly!**

### Step 2: Test in Serial Monitor

**In Arduino IDE Serial Monitor:**

1. Type `w` and press Enter
2. **You should see:** `FWD`
3. Type `s` and press Enter  
4. **You should see:** `REV`
5. Type `a` and press Enter
6. **You should see:** `LEFT TAP`

**If this works → Sketch is fine, Python communication issue**
**If this doesn't work → Sketch problem, re-upload**

### Step 3: Test on Raspberry Pi via SSH

**SSH into Pi:**
```bash
ssh pi@raspberrypi.local
cd ~/b-bots
```

**Run verification:**
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
1. Close Serial Monitor in Arduino IDE (only one program can use serial at a time!)
2. Wait 5 seconds
3. Run verification again

### Step 4: Test Communication

```bash
python3 controls/test_communication.py
```

This will:
- Check for startup messages
- Test all commands
- Show exactly what responses are received

### Step 5: Monitor Serial in Real-Time

**Terminal 1 (SSH):**
```bash
python3 controls/debug_serial.py --port /dev/ttyACM0
```

**Terminal 2 (SSH):**
```bash
python3 controls/arduino_wasd_controller.py --port /dev/ttyACM0 --debug w
```

**You should see in Terminal 1:**
- Startup messages when connection opens
- "FWD" when command is sent

## Common Issues

### Issue 1: Serial Monitor is Open

**Problem:** Arduino IDE Serial Monitor is using the port

**Solution:**
1. Close Serial Monitor in Arduino IDE
2. Wait a few seconds
3. Try Python script again

**Check:**
```bash
# See what's using the port
lsof /dev/ttyACM0
```

### Issue 2: Arduino Resets on Connection

**This is NORMAL!** Arduino resets when serial connection opens.

**Solution:** Code already handles this with 2-3 second wait.

### Issue 3: No Startup Messages

**Problem:** Sketch isn't running or not sending messages

**Solutions:**
1. Re-upload sketch
2. Check Serial Monitor shows messages
3. Verify baud rate is 9600
4. Check `Serial.begin(9600)` is in setup()

### Issue 4: Commands Sent But No Response

**Problem:** Arduino receives but doesn't respond

**Check:**
1. Serial Monitor - send commands manually
2. Do you see responses in Serial Monitor?
3. If yes → Python timing issue
4. If no → Sketch issue

## Quick Test Commands

### Test 1: Verify Sketch
```bash
python3 controls/verify_sketch.py
```

### Test 2: Test Communication
```bash
python3 controls/test_communication.py
```

### Test 3: Monitor Serial
```bash
# Terminal 1
python3 controls/debug_serial.py

# Terminal 2  
python3 controls/arduino_wasd_controller.py w
```

### Test 4: Check Arduino Directly
```bash
# Send command and see response
python3 controls/arduino_wasd_controller.py --port /dev/ttyACM0 --debug w
```

## Expected Behavior

### ✅ Working Correctly:

1. **Startup:**
   - Arduino sends "WASD + Test Mode Ready"
   - Help text appears
   - Python receives these messages

2. **Commands:**
   - Send 'w' → Receive "FWD"
   - Send 's' → Receive "REV"  
   - Send 'a' → Receive "LEFT TAP"
   - Send 'd' → Receive "RIGHT TAP"

3. **Hardware:**
   - Motors move (if connected)
   - LED flashes (if on pin 13)

### ⚠️ If No Responses:

**But Serial Monitor works:**
- Python timing issue
- Port conflict
- Buffer issues

**But Serial Monitor doesn't work:**
- Sketch not uploaded
- Sketch not running
- Hardware issue

## Debugging Workflow

### Workflow 1: Verify Sketch First

```bash
# 1. On laptop: Open Arduino IDE Serial Monitor
#    - Should see "WASD + Test Mode Ready"
#    - Test commands manually
#    - Close Serial Monitor

# 2. On Pi via SSH:
python3 controls/verify_sketch.py

# 3. If no startup messages:
#    - Re-upload sketch
#    - Check Serial Monitor again
#    - Verify baud rate

# 4. If startup messages but no command responses:
#    - Check timing
#    - Use debug_serial.py to monitor
#    - Test commands manually
```

### Workflow 2: Test Communication

```bash
# 1. Make sure Serial Monitor is closed

# 2. Test communication
python3 controls/test_communication.py

# 3. Monitor serial in real-time
python3 controls/debug_serial.py

# 4. In another terminal, send commands
python3 controls/arduino_wasd_controller.py --debug w
```

## Next Steps

Once communication works:

1. **Test all commands:**
   ```bash
   python3 controls/test_communication.py
   ```

2. **Run interactive control:**
   ```bash
   python3 controls/interactive_control.py
   ```

3. **Verify motors work:**
   - Send commands
   - Check motor movement
   - Test steering

## Critical Checkpoints

### Checkpoint 1: Serial Monitor Works?
- ✅ Yes → Python communication issue
- ❌ No → Sketch issue, re-upload

### Checkpoint 2: Startup Messages Received?
- ✅ Yes → Sketch is running
- ❌ No → Sketch not running, re-upload

### Checkpoint 3: Command Responses Received?
- ✅ Yes → Everything works!
- ❌ No → Check timing, buffers, or sketch

## Quick Reference

```bash
# Verify sketch
python3 controls/verify_sketch.py

# Test communication  
python3 controls/test_communication.py

# Monitor serial
python3 controls/debug_serial.py

# Send test command
python3 controls/arduino_wasd_controller.py --debug w

# Check ports
python3 controls/arduino_wasd_controller.py --list-ports
```

