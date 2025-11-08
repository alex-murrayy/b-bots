# Pin Mapping Guide

## Current Issue
Controls are reversed/mixed up because pin assignments don't match the actual wiring.

## How to Fix

### Step 1: Use Test Mode to Identify Pins
1. Upload the sketch with test mode
2. Enter test mode by sending 't' command
3. Test each pin:
   - Send '1' → Check which motor activates (should be forward)
   - Send '2' → Check which motor activates (should be reverse)
   - Send '3' → Check which motor activates (should be left)
   - Send '4' → Check which motor activates (should be right)
4. Note which physical motor each test activates

### Step 2: Update Pin Assignments
Based on your test results, update the pin numbers in `arduinoControls.ino`:

```cpp
const int PIN_FWD   = X;  // Replace X with pin that activates forward motor
const int PIN_REV   = Y;  // Replace Y with pin that activates reverse motor
const int PIN_LEFT  = Z;  // Replace Z with pin that activates left motor
const int PIN_RIGHT = W;  // Replace W with pin that activates right motor
```

### Step 3: Upload and Test
1. Upload the updated sketch
2. Test with: `python3 controls/test_arduino.py`
3. Verify controls work correctly

## Current Behavior Analysis
Based on your report:
- 'w' (forward command) → turns left → Pin 5 is LEFT motor
- 'a' (left command) → goes forward → Pin 8 is FORWARD motor
- 'd' (right command) → reverses → Pin 6 is REVERSE motor
- Right not working → Pin 7 should be RIGHT motor (check wiring)

## Fixed Pin Mapping
The sketch has been updated with:
```
PIN_FWD   = 8  (because pin 8 activates forward)
PIN_REV   = 6  (because pin 6 activates reverse)
PIN_LEFT  = 5  (because pin 5 activates left)
PIN_RIGHT = 7  (because pin 7 should activate right)
```

## If Right Still Doesn't Work
1. Check wiring on pin 7
2. Test pin 7 directly in test mode (send '4')
3. Verify the right motor is connected correctly
4. Check if ACTIVE_LOW needs to be set to true

## Troubleshooting
- If controls are still wrong, use test mode to verify which pin controls which motor
- Check if ACTIVE_LOW should be true (some motor drivers are inverted)
- Verify all connections are secure
- Check motor driver board configuration

