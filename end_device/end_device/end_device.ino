/*****************************************************************
Connor Burken
cburke8
end_device.ino
CS498 IoT Lab 2
UIUC FA20 

Description: This software handles the XBee communication, and
smoke detection, and air quality detection. It reports this 
information to the coordinator (RPi).
*****************************************************************/
#include <SoftwareSerial.h>

#define ATMEGA328P_RX0  2
#define ATMEGA328P_TX0  3
#define ARDUINO_UNO_RX0 2
#define ARDUINO_UNO_TX0 3
#define ATMEGA2560_RX0  10
#define ATMEGA2560_TX0  11

int airSensorValue;
int smokeSensorValue;

#define BAUDRATE 9600


void setup()
{
  // Set up both ports at 9600 baud. This value is most important
  // for the XBee. Make sure the baud rate matches the config
  // setting of your XBee.

  Serial.begin(BAUDRATE);
}

void update_air_sensor()
{
  airSensorValue = analogRead(0);
}

void update_smoke_sensor()
{
  smokeSensorValue = analogRead(1);
}



void sendMessages()
{
   Serial.println("{ \"Id\" : \"air_sensor\" , \"sensor_value\" :" + String(airSensorValue) + " }");
   Serial.println("{ \"Id\" : \"smoke_sensor\" , \"sensor_value\" :" + String(smokeSensorValue) + " }");
}

void loop()
{
  update_air_sensor();
  update_smoke_sensor();
  sendMessages();
  delay(1000);

}
