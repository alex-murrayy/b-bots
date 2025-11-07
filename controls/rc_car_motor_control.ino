/*
 * RC Car Motor Control for Arduino Uno R4
 * Single Drive Motor + Servo Steering Configuration
 * Compatible with L298N, TB6612FNG, DRV8833, and similar motor drivers
 * 
 * Motor Driver Connections:
 * - Drive Motor:  IN1, IN2, ENA (forward/reverse control)
 * - Steering Servo: Servo control pin
 * 
 * Serial Commands:
 * - "F<speed>" - Forward (speed: 0-255)
 * - "B<speed>" - Backward (speed: 0-255)
 * - "S" - Stop
 * - "ST<angle>" - Set Steering Angle (0-180 degrees, 90 = center)
 * - "L<angle>" - Turn Left (sets steering angle left of center)
 * - "R<angle>" - Turn Right (sets steering angle right of center)
 */

#include <Servo.h>

// ============================================================================
// MOTOR DRIVER CONFIGURATION
// ============================================================================
// Uncomment the motor driver you're using, or configure manually below

// For L298N / L293D H-Bridge (Single Motor)
#define DRIVER_L298N

// For TB6612FNG (Single Motor Channel)
// #define DRIVER_TB6612

// For DRV8833 (Single Motor Channel)
// #define DRIVER_DRV8833

// ============================================================================
// PIN DEFINITIONS
// ============================================================================

// Drive Motor Pins (Forward/Reverse)
#ifdef DRIVER_L298N
  const int DRIVE_MOTOR_PIN1 = 2;    // IN1 - Direction control 1
  const int DRIVE_MOTOR_PIN2 = 4;    // IN2 - Direction control 2
  const int DRIVE_MOTOR_PWM = 5;     // ENA - Speed control (PWM)
#elif defined(DRIVER_TB6612)
  const int DRIVE_MOTOR_PIN1 = 2;    // AIN1
  const int DRIVE_MOTOR_PIN2 = 4;    // AIN2
  const int DRIVE_MOTOR_PWM = 5;     // PWMA
#elif defined(DRIVER_DRV8833)
  const int DRIVE_MOTOR_PIN1 = 2;    // AIN1
  const int DRIVE_MOTOR_PIN2 = 4;    // AIN2
  const int DRIVE_MOTOR_PWM = 5;     // Not used (PWM on pin1/pin2)
#endif

// Steering Servo Pin
const int STEERING_SERVO_PIN = 10;

// Standby/Enable pin (if your driver has one, like TB6612FNG)
const int STBY_PIN = 12;  // Set to -1 if not used

// Steering Configuration
const int STEERING_CENTER = 90;      // Center steering position
const int STEERING_MAX_LEFT = 45;    // Maximum left turn
const int STEERING_MAX_RIGHT = 135;  // Maximum right turn

// ============================================================================
// GLOBAL VARIABLES
// ============================================================================

Servo steeringServo;
int currentSpeed = 0;
int steeringAngle = STEERING_CENTER;  // Center position
String serialBuffer = "";

// ============================================================================
// SETUP
// ============================================================================

void setup() {
  // Initialize Serial Communication
  Serial.begin(115200);
  Serial.setTimeout(50);  // Set timeout for reading serial data
  Serial.println("RC Car Motor Control System Initialized");
  Serial.println("Configuration: Single Drive Motor + Servo Steering");
  Serial.println("Ready for commands...");
  
  // Initialize Drive Motor Pins
  pinMode(DRIVE_MOTOR_PIN1, OUTPUT);
  pinMode(DRIVE_MOTOR_PIN2, OUTPUT);
  
  if (DRIVE_MOTOR_PWM >= 0) {
    pinMode(DRIVE_MOTOR_PWM, OUTPUT);
  }
  
  // Initialize Standby Pin (if used)
  if (STBY_PIN >= 0) {
    pinMode(STBY_PIN, OUTPUT);
    digitalWrite(STBY_PIN, HIGH);  // Enable driver
  }
  
  // Initialize Steering Servo
  steeringServo.attach(STEERING_SERVO_PIN);
  steeringServo.write(steeringAngle);  // Center steering
  
  // Stop drive motor
  stopMotor();
  
  Serial.println("Setup complete. Send commands via Serial:");
  Serial.println("  F<speed> - Forward (0-255)");
  Serial.println("  B<speed> - Backward (0-255)");
  Serial.println("  S - Stop");
  Serial.println("  ST<angle> - Set Steering (0-180, 90=center)");
  Serial.println("  L<angle> - Turn Left (offset from center)");
  Serial.println("  R<angle> - Turn Right (offset from center)");
}

// ============================================================================
// MAIN LOOP
// ============================================================================

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    command.toUpperCase();
    
    if (command.length() > 0) {
      processCommand(command);
    }
  }
  
  // Small delay to prevent overwhelming the processor
  delay(10);
}

// ============================================================================
// COMMAND PROCESSING
// ============================================================================

void processCommand(String cmd) {
  if (cmd.length() == 0) return;
  
  char action = cmd.charAt(0);
  String value = cmd.substring(1);
  
  switch (action) {
    case 'F':  // Forward
      {
        int speed = value.toInt();
        speed = constrain(speed, 0, 255);
        moveForward(speed);
        Serial.print("Forward: ");
        Serial.println(speed);
      }
      break;
      
    case 'B':  // Backward
      {
        int speed = value.toInt();
        speed = constrain(speed, 0, 255);
        moveBackward(speed);
        Serial.print("Backward: ");
        Serial.println(speed);
      }
      break;
      
    case 'S':  // Stop
      stopMotor();
      Serial.println("Stop");
      break;
      
    case 'T':  // Steering (ST<angle>)
      if (cmd.startsWith("ST")) {
        int angle = cmd.substring(2).toInt();
        angle = constrain(angle, 0, 180);
        setSteering(angle);
        Serial.print("Steering: ");
        Serial.println(angle);
      }
      break;
      
    case 'L':  // Turn Left (relative to center)
      {
        int offset = value.toInt();
        offset = constrain(offset, 0, 45);  // Max 45 degrees from center
        int angle = STEERING_CENTER - offset;
        angle = constrain(angle, STEERING_MAX_LEFT, STEERING_CENTER);
        setSteering(angle);
        Serial.print("Turn Left: ");
        Serial.print(offset);
        Serial.print(" degrees (Angle: ");
        Serial.print(angle);
        Serial.println(")");
      }
      break;
      
    case 'R':  // Turn Right (relative to center)
      {
        int offset = value.toInt();
        offset = constrain(offset, 0, 45);  // Max 45 degrees from center
        int angle = STEERING_CENTER + offset;
        angle = constrain(angle, STEERING_CENTER, STEERING_MAX_RIGHT);
        setSteering(angle);
        Serial.print("Turn Right: ");
        Serial.print(offset);
        Serial.print(" degrees (Angle: ");
        Serial.print(angle);
        Serial.println(")");
      }
      break;
      
    default:
      Serial.print("Unknown command: ");
      Serial.println(cmd);
      printHelp();
      break;
  }
}

// ============================================================================
// MOTOR CONTROL FUNCTIONS
// ============================================================================

void setDriveMotor(int speed) {
  // Constrain speed to valid range
  speed = constrain(speed, -255, 255);
  
  // Set direction and speed
  if (speed > 0) {
    // Forward
    digitalWrite(DRIVE_MOTOR_PIN1, HIGH);
    digitalWrite(DRIVE_MOTOR_PIN2, LOW);
    if (DRIVE_MOTOR_PWM >= 0) {
      analogWrite(DRIVE_MOTOR_PWM, speed);
    }
  } else if (speed < 0) {
    // Backward
    digitalWrite(DRIVE_MOTOR_PIN1, LOW);
    digitalWrite(DRIVE_MOTOR_PIN2, HIGH);
    if (DRIVE_MOTOR_PWM >= 0) {
      analogWrite(DRIVE_MOTOR_PWM, -speed);
    }
  } else {
    // Stop
    digitalWrite(DRIVE_MOTOR_PIN1, LOW);
    digitalWrite(DRIVE_MOTOR_PIN2, LOW);
    if (DRIVE_MOTOR_PWM >= 0) {
      analogWrite(DRIVE_MOTOR_PWM, 0);
    }
  }
}

void moveForward(int speed) {
  setDriveMotor(speed);
  currentSpeed = speed;
}

void moveBackward(int speed) {
  setDriveMotor(-speed);
  currentSpeed = -speed;
}

void stopMotor() {
  setDriveMotor(0);
  currentSpeed = 0;
}

// ============================================================================
// STEERING CONTROL
// ============================================================================

void setSteering(int angle) {
  angle = constrain(angle, 0, 180);
  steeringAngle = angle;
  steeringServo.write(angle);
}

int getSteering() {
  return steeringAngle;
}

void centerSteering() {
  setSteering(STEERING_CENTER);
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

void printStatus() {
  Serial.println("=== RC Car Status ===");
  Serial.print("Speed: ");
  Serial.println(currentSpeed);
  Serial.print("Steering Angle: ");
  Serial.println(steeringAngle);
  Serial.println("===================");
}

void printHelp() {
  Serial.println("Available commands:");
  Serial.println("  F<speed> - Forward (0-255)");
  Serial.println("  B<speed> - Backward (0-255)");
  Serial.println("  S - Stop");
  Serial.println("  ST<angle> - Set Steering (0-180, 90=center)");
  Serial.println("  L<angle> - Turn Left (0-45 degrees from center)");
  Serial.println("  R<angle> - Turn Right (0-45 degrees from center)");
}
