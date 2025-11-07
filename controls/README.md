# RC Car Motor Control - Arduino Sketch

Arduino Uno R4 sketch for controlling RC car with single drive motor and servo steering via serial commands.

## Hardware Requirements

- **Arduino Uno R4** (or compatible)
- **Motor Driver Board** (L298N, TB6612FNG, DRV8833, or similar)
- **1x DC Motor** for drive (forward/reverse)
- **1x Servo Motor** for steering
- **Power Supply** (appropriate for your motors)

## Wiring Guide

### Motor Driver Connections

#### L298N / L293D Configuration (Single Motor)
```
Drive Motor:
- IN1 → Arduino Pin 2
- IN2 → Arduino Pin 4
- ENA → Arduino Pin 5 (PWM)
- Motor + → OUT1
- Motor - → OUT2

Power:
- VCC → 5V (if needed for logic)
- GND → GND
- Motor Power → External power supply (7-12V typical)
```

#### TB6612FNG Configuration (Single Motor Channel)
```
Drive Motor (Motor A):
- AIN1 → Arduino Pin 2
- AIN2 → Arduino Pin 4
- PWMA → Arduino Pin 5 (PWM)
- AO1 → Drive Motor +
- AO2 → Drive Motor -

Control:
- STBY → Arduino Pin 12
- VM → Motor Power (2.5V-13.5V)
- VCC → 5V
- GND → GND
```

#### Steering Servo
```
Servo Motor:
- Signal → Arduino Pin 10
- Power → 5V (or external supply if needed)
- Ground → GND
```

## Serial Commands

The sketch accepts the following commands via Serial (115200 baud):

| Command | Description | Example |
|---------|-------------|---------|
| `F<speed>` | Move Forward | `F200` (forward at speed 200) |
| `B<speed>` | Move Backward | `B150` (backward at speed 150) |
| `S` | Stop | `S` |
| `ST<angle>` | Set Steering Angle | `ST90` (center), `ST45` (left), `ST135` (right) |
| `L<angle>` | Turn Left (relative) | `L30` (30 degrees left from center) |
| `R<angle>` | Turn Right (relative) | `R30` (30 degrees right from center) |

### Command Details

- **Speed Range**: 0-255 (0 = stop, 255 = full speed)
- **Steering Angle**: 0-180 degrees (90 = center, 0-45 = left range, 135-180 = right range)
- **Turn Commands (L/R)**: 0-45 degrees offset from center

### Example Commands

```bash
# Move forward at half speed
F128

# Turn left while moving forward
ST45
F200

# Turn right using relative command
R30
F200

# Stop
S

# Set steering to center
ST90

# Move backward
B150
```

## Configuration

### Selecting Your Motor Driver

Edit the sketch and uncomment the appropriate driver define:

```cpp
// For L298N / L293D
#define DRIVER_L298N

// For TB6612FNG
// #define DRIVER_TB6612

// For DRV8833
// #define DRIVER_DRV8833
```

### Pin Configuration

If your wiring differs, modify the pin definitions in the sketch:

```cpp
// Drive Motor Pins
const int DRIVE_MOTOR_PIN1 = 2;
const int DRIVE_MOTOR_PIN2 = 4;
const int DRIVE_MOTOR_PWM = 5;

// Steering Servo
const int STEERING_SERVO_PIN = 10;

// Standby Pin (if used by your driver)
const int STBY_PIN = 12;
```

## Testing

1. **Upload the sketch** to your Arduino Uno R4
2. **Open Serial Monitor** (Tools → Serial Monitor)
3. **Set baud rate** to 115200
4. **Send test commands**:
   - `F100` - Should move forward slowly
   - `ST45` - Should turn steering left
   - `S` - Should stop

## Integration with Python Delivery System

You can integrate this with the Python delivery system by creating a serial communication module:

```python
import serial
import time

class RCCarController:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        self.serial = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for Arduino to initialize
    
    def forward(self, speed=200):
        """Move forward at specified speed (0-255)"""
        self.serial.write(f'F{speed}\n'.encode())
        time.sleep(0.1)  # Small delay for command processing
    
    def backward(self, speed=200):
        """Move backward at specified speed (0-255)"""
        self.serial.write(f'B{speed}\n'.encode())
        time.sleep(0.1)
    
    def stop(self):
        """Stop the drive motor"""
        self.serial.write('S\n'.encode())
        time.sleep(0.1)
    
    def set_steering(self, angle):
        """Set steering angle (0-180, 90=center)"""
        angle = max(0, min(180, angle))  # Constrain to 0-180
        self.serial.write(f'ST{angle}\n'.encode())
        time.sleep(0.1)
    
    def turn_left(self, angle_offset=30):
        """Turn left by specified degrees from center (0-45)"""
        angle_offset = max(0, min(45, angle_offset))
        self.serial.write(f'L{angle_offset}\n'.encode())
        time.sleep(0.1)
    
    def turn_right(self, angle_offset=30):
        """Turn right by specified degrees from center (0-45)"""
        angle_offset = max(0, min(45, angle_offset))
        self.serial.write(f'R{angle_offset}\n'.encode())
        time.sleep(0.1)
    
    def center_steering(self):
        """Center the steering"""
        self.set_steering(90)
    
    def close(self):
        """Close serial connection"""
        self.stop()
        self.center_steering()
        self.serial.close()

# Example usage
if __name__ == '__main__':
    car = RCCarController('/dev/ttyUSB0')  # Adjust port for your system
    try:
        # Move forward with steering
        car.forward(200)
        car.set_steering(45)  # Turn left
        time.sleep(2)
        
        # Center and continue
        car.center_steering()
        time.sleep(1)
        
        # Stop
        car.stop()
    finally:
        car.close()
```

## Troubleshooting

### Motors Not Responding
- Check power supply connections
- Verify motor driver is enabled (STBY pin for TB6612FNG)
- Check pin connections match the sketch configuration
- Ensure motor driver has sufficient power (check voltage requirements)

### Motor Running in Wrong Direction
- Swap the motor wires connected to the driver outputs, OR
- Swap DRIVE_MOTOR_PIN1 and DRIVE_MOTOR_PIN2 connections in the sketch

### Servo Not Responding
- Check servo signal wire is on correct pin
- Verify servo power supply (may need external 5V supply)
- Check servo angle range (typically 0-180 degrees)

### Serial Communication Issues
- Verify baud rate is set to 115200
- Check USB cable connection
- Ensure no other program is using the serial port

## Safety Notes

- Always test with low speeds first
- Ensure adequate power supply for motors
- Use appropriate fuses for overcurrent protection
- Be careful with high-speed movements during testing
- Keep hands clear of moving parts during operation

## License

This code is provided as-is for educational and development purposes.

