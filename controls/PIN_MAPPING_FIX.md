# Pin Mapping Fix

## Problem
Controls were reversed/mixed up:
- Forward ('w') was turning left
- Left ('a') was going forward
- Right ('d') was reversing
- Right steering wasn't working

## Solution
The pin assignments in `arduinoControls.ino` have been updated to match the actual wiring.

## New Pin Mapping
```
PIN_FWD   = 8  (Forward motor)
PIN_REV   = 6  (Reverse motor)
PIN_LEFT  = 5  (Left steering)
PIN_RIGHT = 7  (Right steering)
```

## Testing
1. Upload the updated `arduinoControls.ino` sketch
2. Test with: `python3 controls/test_arduino.py --debug`
3. Verify:
   - 'w' moves forward
   - 's' moves backward
   - 'a' turns left
   - 'd' turns right

## If Still Wrong
If controls are still incorrect, you can use Test Mode to verify which pin controls which motor:

1. Enter test mode: Send 't' command
2. Test each pin:
   - '1' = PIN_FWD (should move forward)
   - '2' = PIN_REV (should move backward)
   - '3' = PIN_LEFT (should turn left)
   - '4' = PIN_RIGHT (should turn right)
3. Exit test mode: Send 'q'

Then adjust the pin numbers in `arduinoControls.ino` to match what you observe.

