#include <AFMotor.h>

#define IR_SENSOR_RIGHT 49
#define IR_SENSOR_LEFT 47
#define trigpin A14
#define echopin A15

int distance;
float duration;

AF_DCMotor motor1(1); // create motor #1, labeled M1 on the shield left motor
AF_DCMotor motor2(4); // create motor #2, labeled M2 on the shield right motor

void setup()
{
  Serial.begin(9600); // Initialize serial communication

  pinMode(trigpin, OUTPUT);
  pinMode(echopin, INPUT);
  pinMode(IR_SENSOR_RIGHT, INPUT);
  pinMode(IR_SENSOR_LEFT, INPUT);

  motor1.run(RELEASE);
  motor1.setSpeed(120); // Set speed of motor1 (0-255)
  motor2.run(RELEASE);
  motor2.setSpeed(120); // Set speed of motor2 (0-255)
}

void loop()
{


  int rightIRSensorValue = digitalRead(IR_SENSOR_RIGHT);
  int leftIRSensorValue = digitalRead(IR_SENSOR_LEFT);

  // Measure distance using ultrasonic sensor
  digitalWrite(trigpin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigpin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigpin, LOW);
  duration = pulseIn(echopin, HIGH);
  distance = duration * 0.034 / 2;

  Serial.print("Distance: ");
  Serial.println(distance);

  // If distance is 7cm or less, release both motors
  if (distance <= 7)
  {
    motor1.run(RELEASE);
    motor2.run(RELEASE);
    Serial.println("Motors released");
  }
  else
  {
    // If none of the sensors detects a black line, then go straight
    if (rightIRSensorValue == LOW && leftIRSensorValue == LOW)
    {
      motor1.run(FORWARD);
      motor2.run(FORWARD);
      motor1.setSpeed(120); // Set speed of motor1 (0-255)
      motor2.setSpeed(120);
    }
    // If right sensor detects a black line, then turn right
    else if (rightIRSensorValue == HIGH && leftIRSensorValue == LOW)
    {
      motor1.run(FORWARD);
      motor2.run(BACKWARD);
      motor1.setSpeed(120); // Set speed of motor1 (0-255)
      motor2.setSpeed(60);  // Set speed of motor2 (0-255)
    }
    // If left sensor detects a black line, then turn left
    else if (rightIRSensorValue == LOW && leftIRSensorValue == HIGH)
    {
      motor1.run(BACKWARD);
      motor2.run(FORWARD);
      motor1.setSpeed(60);  // Set speed of motor1 (0-255)
      motor2.setSpeed(120); // Set speed of motor2 (0-255)
    }
    // If both sensors detect a black line, then stop
    else
    {
      motor1.run(RELEASE);
      motor2.run(RELEASE);
    }
  }
}
