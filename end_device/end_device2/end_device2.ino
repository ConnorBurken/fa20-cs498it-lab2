/*****************************************************************
Connor Burken
cburke8
end_device.ino
CS498 IoT Lab 2
UIUC FA20 

Description: This software handles the XBee communication, and
sound detection. It reports this 
information to the coordinator (RPi).
*****************************************************************/
#include <SoftwareSerial.h>
#define PIN_GATE_IN 2
#define IRQ_GATE_IN  0
#define PIN_LED_OUT 13
#define PIN_ANALOG_IN A0

int soundSensorValue;

#define BAUDRATE 9600


void setup()
{
  // Set up both ports at 9600 baud. This value is most important
  // for the XBee. Make sure the baud rate matches the config
  // setting of your XBee.

  Serial.begin(BAUDRATE);
  pinMode(PIN_GATE_IN, INPUT);

  attachInterrupt(IRQ_GATE_IN, soundISR, CHANGE);

  // Display status
  Serial.println("Initialized");
}

void update_sound_sensor()
{
  soundSensorValue = analogRead(0);
}


void soundISR()
{
  int pin_val;

  pin_val = digitalRead(PIN_GATE_IN); 
}


void sendMessages()
{
   Serial.println("{ \"Id\" : \"sound_sensor\" , \"sensor_value\" :" + String(soundSensorValue) + " }");
}

void loop()
{
  update_sound_sensor();
  sendMessages();
  delay(1000);

}
