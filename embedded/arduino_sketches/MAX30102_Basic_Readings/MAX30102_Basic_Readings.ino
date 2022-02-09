/*
  MAX30105 Breakout: Output all the raw Red/IR/Green readings
  By: Nathan Seidle @ SparkFun Electronics
  Date: October 2nd, 2016
  https://github.com/sparkfun/MAX30105_Breakout

  Outputs all Red/IR/Green values.

  Hardware Connections (Breakoutboard to Arduino):
  -5V = 5V (3.3V is allowed)
  -GND = GND
  -SDA = A4 (or SDA)
  -SCL = A5 (or SCL)
  -INT = Not connected

  The MAX30105 Breakout can handle 5V or 3.3V I2C logic. We recommend powering the board with 5V
  but it will also run at 3.3V.

  This code is released under the [MIT License](http://opensource.org/licenses/MIT).
*/

/*
  NOTE:

  This is a modified version of the Example1_Basic_Readings from the Sparkfun MAX30102 Library.
  This version will meassure the time since the meassurements starts and count the meassured samples.
  It will print the serial data in the format:
  millis, ir, red, sample

  Additionally it has an extra function pollSerial which polls from the Serial input.
  On the computer there might be a python script running which wants to reset the meassurement.
*/

#include <Wire.h>
#include "MAX30105.h"

MAX30105 particleSensor;
unsigned long t_run;
unsigned long t_start;
unsigned int n_samples;

#define debug Serial //Uncomment this line if you're using an Uno or ESP
//#define debug SerialUSB //Uncomment this line if you're using a SAMD21

void setup()
{

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  debug.begin(9600);

  // Initialize sensor
  if (particleSensor.begin() == false)
  {
    debug.println("MAX30105 was not found. Please check wiring/power. ");
    while (1);
  }

    //Let's configure the sensor to run fast so we can over-run the buffer and cause an interrupt
  byte ledBrightness = 0x66; //Options: 0=Off to 255=50mA
  byte sampleAverage = 4; //Options: 1, 2, 4, 8, 16, 32
  byte ledMode = 1; //Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green
  byte sampleRate = 1000; //Options: 50, 100, 200, 400, 800, 1000, 1600, 3200
  int pulseWidth = 411; //Options: 69, 118, 215, 411
  int adcRange = 2048; //Options: 2048, 4096, 8192, 16384
  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange); //Configure sensor with these settings

  n_samples = 0;
  t_start = millis();
}

// Polls the serial port and restart messaruement
void pollSerial() {

  if (debug.available()) {
    int reading = Serial.readString().toInt();

    if (reading == 0)
      digitalWrite(LED_BUILTIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(LED_BUILTIN, LOW);

    // Start the meassurement again.
    t_start = millis();
    n_samples = 0;
  }
}

void loop()
{
  pollSerial();
  t_run = millis() - t_start;
  debug.print("Millis=");
  debug.print(t_run);
  debug.print(",Red=");
  debug.print(particleSensor.getRed());
  debug.print(",IR=");
  debug.print(particleSensor.getIR());
  debug.print(",samples=");
  debug.print(n_samples++);
  debug.println();
}
