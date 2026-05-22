#include <Arduino.h>
#include <Stepper.h>

// --- PIN DEFINITIONS ---
#define TRIG_PIN 2
#define ECHO_PIN 3
#define LDR_LEFT A0
#define LDR_RIGHT A1
#define TEMP_PIN A2

// --- STEPPER CONFIGURATION ---
const int stepsPerRevolution = 2048; // Standard 28BYJ-48 stepper
// NOTE: The ULN2003 driver requires the pin sequence 1-3-2-4 for the default Stepper.h library
Stepper myStepper(stepsPerRevolution, 8, 10, 9, 11); 

// --- RADAR GIMBAL VARIABLES ---
int sweepLimit = 85; // ~15 degree arc
int currentPosition = 0;
int sweepDirection = 1; // 1 for right, -1 for left

void setup() {
  // 115200 Baud is critical. 9600 is too slow for machine learning telemetry.
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  myStepper.setSpeed(15); // 15 RPM for a smooth, deliberate radar sweep
}

// Custom Ultrasonic Function to prevent blocking the motor
float getDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // 30ms timeout so the loop doesn't freeze if it points at the ceiling
  long duration = pulseIn(ECHO_PIN, HIGH, 30000); 
  if(duration == 0) return -1.0; // Out of range flag
  return duration * 0.034 / 2.0;
}

// Convert LM35 analog reading to Celsius
float getTemperature() {
  int raw = analogRead(TEMP_PIN);
  float voltage = raw * (5.0 / 1023.0);
  return voltage * 100.0;
}

void loop() {
  // 1. ACTUATE GIMBAL
  // Move 5 micro-steps at a time to prevent stuttering
  myStepper.step(sweepDirection * 5);
  currentPosition += (sweepDirection * 5);

  // Reverse direction if we hit the 15-degree limit
  if (currentPosition >= sweepLimit || currentPosition <= -sweepLimit) {
    sweepDirection *= -1; 
  }

  // 2. FIRE SENSOR ARRAY
  float distance = getDistance();
  int ldrLeft = analogRead(LDR_LEFT);
  int ldrRight = analogRead(LDR_RIGHT);
  float temp = getTemperature();

  // 3. BLAST TELEMETRY TO PYTHON
  // Format: Distance, LDR_Left, LDR_Right, Temperature
  Serial.print(distance);
  Serial.print(",");
  Serial.print(ldrLeft);
  Serial.print(",");
  Serial.print(ldrRight);
  Serial.print(",");
  Serial.println(temp);

  // 4. LOCK THE SAMPLING RATE
  // Forces the system to sample at roughly 10Hz. Crucial for CNN time-series.
  delay(50); 
}