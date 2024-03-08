#include <AccelStepper.h>

//j3 = StepperMotor(dir_pin=33, step_pin=15, enable_pin = 18, gearRatio=1)

#define J0_DIR_PIN 26     // Define accordingly
#define J0_STEP_PIN 25    // Define accordingly
#define J0_ENABLE_PIN 13  // Define accordingly

#define J1_DIR_PIN 17
#define J1_STEP_PIN 21
#define J1_ENABLE_PIN 16

#define J2_DIR_PIN 32
#define J2_STEP_PIN 14
#define J2_ENABLE_PIN 19

#define J3_DIR_PIN 33
#define J3_STEP_PIN 15
#define J3_ENABLE_PIN 18

// Microstepping mode ratios, assuming a 1/4 step as default
#define MICROSTEPPING 16

// Gear ratio and steps per revolution for J1 and J2
#define GEAR_RATIO 26
#define STEPS_PER_REVOLUTION 200

// Calculate total steps considering gear ratio and microstepping
#define TOTAL_STEPS_PER_REVOLUTION (STEPS_PER_REVOLUTION * GEAR_RATIO * MICROSTEPPING)
#define TOTAL_STEPS_PER_REVOLUTION_PEN (STEPS_PER_REVOLUTION * MICROSTEPPING)

float J0Angle = 0;
float J1Angle = 0;
float J2Angle = 0;
float J3Angle = 0;

const float MAX_SAFE_SPEED = 5000.0;        // Steps per second
const float MAX_SAFE_ACCELERATION = 5000.0;  // Steps per second squared

// Initialize AccelStepper
AccelStepper stepperJ0(1, J0_STEP_PIN, J0_DIR_PIN);
AccelStepper stepperJ1(1, J1_STEP_PIN, J1_DIR_PIN);
AccelStepper stepperJ2(1, J2_STEP_PIN, J2_DIR_PIN);
AccelStepper stepperJ3(1, J3_STEP_PIN, J3_DIR_PIN);

String inputString = "";      // A String to hold incoming data
bool stringComplete = false;  // Whether the string is complete

void setup() {
  pinMode(J1_ENABLE_PIN, OUTPUT);
  pinMode(J2_ENABLE_PIN, OUTPUT);
  pinMode(J0_ENABLE_PIN, OUTPUT);
  pinMode(J3_ENABLE_PIN, OUTPUT);
  disableMotors();  // Start with the motors disabled

  // Start serial communication at 9600 baud rate
  Serial.begin(115200);
  inputString.reserve(200);  // Reserve 200 bytes for the inputString

  // Set initial motor speed and acceleration
  stepperJ0.setMaxSpeed(1000);     // Steps per second
  stepperJ0.setAcceleration(500);  // Steps per second squared
  stepperJ1.setMaxSpeed(1000);     // Steps per second
  stepperJ1.setAcceleration(500);  // Steps per second squared
  stepperJ2.setMaxSpeed(1000);     // Steps per second
  stepperJ2.setAcceleration(500);  // Steps per second squared
  stepperJ3.setMaxSpeed(1000);     // Steps per second
  stepperJ3.setAcceleration(500);  // Steps per second squared
}

void loop() {
  // Check if data has been received
  if (stringComplete) {
    processInput(inputString);
    // Clear the string for new input
    inputString = "";
    stringComplete = false;
  }
}

void processInput(String input) {
  // Split the input for J1 and J2, expecting format "J1,90;J2,-45;"
  int j0Index = input.indexOf("J0,");
  int j1Index = input.indexOf("J1,");
  int j2Index = input.indexOf("J2,");
  int j3Index = input.indexOf("J3,");
  int zero = input.indexOf("ZERO");
  int home = input.indexOf("HOME");
  float j0Degrees = 0;
  float j1Degrees = 0;
  float j2Degrees = 0;
  float j3Degrees = 0;

  if (j1Index != -1) {
    int semicolonIndex = input.indexOf(";", j1Index);
    String j1Value = input.substring(j1Index + 3, semicolonIndex);
    j1Degrees = j1Value.toFloat();
  }

  if (j2Index != -1) {
    int semicolonIndex = input.indexOf(";", j2Index);
    String j2Value = input.substring(j2Index + 3, semicolonIndex);
    j2Degrees = j2Value.toFloat();
  }

  if (j0Index != -1) {
    int semicolonIndex = input.indexOf(";", j0Index);
    String j0Value = input.substring(j0Index + 3, semicolonIndex);
    j0Degrees = j0Value.toFloat();
  }

  if (j3Index != -1) {
    int semicolonIndex = input.indexOf(";", j3Index);
    String j3Value = input.substring(j3Index + 3, semicolonIndex);
    j3Degrees = j3Value.toFloat();
  }

  if (zero != -1) {
    zeroAngle();
  }

  if (home != -1) {
    j0Degrees = -1*J0Angle;
    j1Degrees = -1*J1Angle;
    j2Degrees = -1*J2Angle;
    j3Degrees = -1*J3Angle;
  }

  J0Angle = J0Angle + j0Degrees;
  J1Angle = J1Angle + j1Degrees;
  J2Angle = J2Angle + j2Degrees;
  J3Angle = J3Angle + j3Degrees;

  long j0Steps = degreesToSteps(j0Degrees);
  long j1Steps = degreesToSteps(j1Degrees);
  long j2Steps = degreesToSteps(j2Degrees);
  long j3Steps = degreesToStepsPen(j3Degrees);
  long maxSteps = max(max(abs(j0Steps), max(abs(j1Steps), abs(j2Steps))), abs(j3Steps));

  float timeToComplete = 1;

  if (maxSteps / timeToComplete > MAX_SAFE_SPEED) {
    timeToComplete = maxSteps / MAX_SAFE_SPEED;
  }

  float speedJ0 = abs(j0Steps / timeToComplete);
  float speedJ1 = abs(j1Steps / timeToComplete);
  float speedJ2 = abs(j2Steps / timeToComplete);
  float speedJ3 = abs(j3Steps / timeToComplete);

  enableMotors();

  stepperJ0.setMaxSpeed(speedJ0);
  stepperJ0.setAcceleration(speedJ0 * 2);  // Adjust as necessary
  stepperJ0.move(j0Steps);

  stepperJ1.setMaxSpeed(speedJ1);
  stepperJ1.setAcceleration(speedJ1 * 2);  // Adjust as necessary
  stepperJ1.move(j1Steps);

  stepperJ2.setMaxSpeed(speedJ2);
  stepperJ2.setAcceleration(speedJ2 * 2);  // Adjust as necessary
  stepperJ2.move(j2Steps);

  stepperJ3.setMaxSpeed(speedJ3);
  stepperJ3.setAcceleration(speedJ3 * 2);  // Adjust as necessary
  stepperJ3.move(j3Steps);

  // Serial.print("Speed J0: ");
  // Serial.println(speedJ0);
  // Serial.print("Steps J0: ");
  // Serial.println(j0Steps);
  // Serial.print("Speed J1: ");
  // Serial.println(speedJ1);
  // Serial.print("Steps J1: ");
  // Serial.println(j2Steps);
  // Serial.print("Speed J2: ");
  // Serial.println(speedJ1);
  // Serial.print("Steps J2: ");
  // Serial.println(j2Steps);
  // Serial.print("Speed J3: ");
  // Serial.println(speedJ3);
  // Serial.print("Steps J3: ");
  // Serial.println(j3Steps);

  // Move both motors
  while (stepperJ0.distanceToGo() != 0 || stepperJ1.distanceToGo() != 0 || stepperJ2.distanceToGo() != 0 || stepperJ3.distanceToGo() != 0) {
    stepperJ0.run();
    stepperJ1.run();
    stepperJ2.run();
    stepperJ3.run();
  }

  updateStatus();

  //disableMotors();  // Disable motors after movement
}

long degreesToSteps(float degrees) {
  // Convert degrees to steps
  return (long)(degrees / 360.0 * TOTAL_STEPS_PER_REVOLUTION);
}

long degreesToStepsPen(float degrees) {
  // Convert degrees to steps
  return (long)(degrees / 360.0 * TOTAL_STEPS_PER_REVOLUTION_PEN);
}

void enableMotors() {
  digitalWrite(J0_ENABLE_PIN, LOW);
  digitalWrite(J1_ENABLE_PIN, LOW);  // Assuming HIGH disables the motor
  digitalWrite(J2_ENABLE_PIN, LOW);
  digitalWrite(J3_ENABLE_PIN, LOW);
}


void disableMotors() {
  digitalWrite(J0_ENABLE_PIN, HIGH);
  digitalWrite(J1_ENABLE_PIN, HIGH);  // Assuming HIGH disables the motor
  digitalWrite(J2_ENABLE_PIN, HIGH);
  digitalWrite(J3_ENABLE_PIN, HIGH);
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == ';') {  // Change to ';' as end of command indicator
      stringComplete = true;
      // Serial.print("Received: ");
      // Serial.println(inputString);
      processInput(inputString);
      inputString = "";  // Clear the string for new input
      stringComplete = false;
    }
  }
}

void zeroAngle() {
  J0Angle = 0;
  J1Angle = 0;
  J2Angle = 0;
  J3Angle = 0;
}

void updateStatus(){
  Serial.print("J0: ");
  Serial.print(J0Angle);
  Serial.print("; J1: ");
  Serial.print(J1Angle);
  Serial.print("; J2: ");
  Serial.print(J2Angle);
  Serial.print("; J3: ");
  Serial.println(J3Angle);
}
