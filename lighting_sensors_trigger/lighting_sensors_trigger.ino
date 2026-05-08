//Fill in pins 2, 3, 4, and 5 with correct pins with our arduino.
//Pins two through 10.
#include "Arduino_LED_Matrix.h"

ArduinoLEDMatrix matrix;

const int red_ns = 2;
const int yellow_ns = 3;
const int green_ns = 4;
const int blue_ns = 5;

const int red_ew = 6;
const int yellow_ew = 7;
const int green_ew = 8;
const int blue_ew = 9;


const int crosswalk_border_crossed = A0;
int crosswalk_border_value = 0;

//12 columns x 8 rows
//"ON"
byte onFrame[8][12] = {
  {0,1,1,0, 0,1,0,0, 0,1,0,0},
  {1,0,0,1, 0,1,1,0, 0,1,0,0},
  {1,0,0,1, 0,1,0,1, 0,1,0,0},
  {1,0,0,1, 0,1,0,0,1,1,0,0},
  {1,0,0,1, 0,1,0,0,0,1,0,0},
  {1,0,0,1, 0,1,0,0,0,1,0,0},
  {1,0,0,1, 0,1,0,0,0,1,0,0},
  {0,1,1,0, 0,1,0,0,0,1,0,0}
};

//"OFF"
byte offFrame[8][12] = {
  {0,1,1,0, 0,1,1,1, 0,1,1,1},
  {1,0,0,1, 0,1,0,0, 0,1,0,0},
  {1,0,0,1, 0,1,0,0, 0,1,0,0},
  {1,0,0,1, 0,1,1,0, 0,1,1,0},
  {1,0,0,1, 0,1,0,0, 0,1,0,0},
  {1,0,0,1, 0,1,0,0, 0,1,0,0},
  {1,0,0,1, 0,1,0,0, 0,1,0,0},
  {0,1,1,0, 0,1,0,0, 0,1,0,0}
};


void setup() 
{
  matrix.begin();
  //Initialize lights as outputs.
  pinMode(red_ns, OUTPUT);
  pinMode(yellow_ns, OUTPUT);
  pinMode(green_ns, OUTPUT);
  pinMode(blue_ns, OUTPUT);

  pinMode(red_ew, OUTPUT);
  pinMode(yellow_ew, OUTPUT);
  pinMode(green_ew, OUTPUT);
  pinMode(blue_ew, OUTPUT);

  //Initialize sensor as input.
  pinMode(crosswalk_border_crossed, INPUT);
  Serial.begin(9600); //115200 //9600 common for printer cable

}

void loop() 
{
  // put your main code here, to run repeatedly:

  //Lights turn on.
  digitalWrite(red_ns, HIGH);
  digitalWrite(yellow_ns, HIGH);
  digitalWrite(green_ns, HIGH);
  digitalWrite(blue_ns, HIGH);
  digitalWrite(red_ew, HIGH);
  digitalWrite(yellow_ew, HIGH);
  digitalWrite(green_ew, HIGH);
  digitalWrite(blue_ew, HIGH);

  showOn();

  Serial.println("lights are On");

  //digitalWrite(light_Yellow, HIGH);
  //digitalWrite(light_Green, HIGH);
  //digitalWrite(light_Blue, HIGH);

 // if(digitalRead(red_ns) == HIGH)
  //{
    //Serial.println("red_ns is on");
  //}

  //else
  //{
    //Serial.println("red_ns is off");
  //}

  //Delay for 1 second, delay(500) is 0.5 seconds
  delay(1000);


 

  //Lights turn off.
  digitalWrite(red_ns, LOW);
  digitalWrite(yellow_ns, LOW);
  digitalWrite(green_ns, LOW);
  digitalWrite(blue_ns, LOW);
  digitalWrite(red_ew, LOW);
  digitalWrite(yellow_ew, LOW);
  digitalWrite(green_ew, LOW);
  digitalWrite(blue_ew, LOW);

  showOff();

  Serial.println("lights are off");

  //Delay for 1 second.
  delay(1000);
  
  //Have a sensor.
  //sensor_VALUE = digitalRead(sensor_PIN_6);
  //
  //if(sensor_VALUE == HIGH)
  //{
    //Serial.println("Detected something.");
  //}

  //else
  //{
    //Serial.println("Nothing detected.");
  //}

  //Have a delay of 0.5 seconds for the sensor.
 // delay(500);


  

}

void showOn(){
  matrix.renderBitmap(onFrame, 8, 12);
}

void showOff(){
  matrix.renderBitmap(offFrame, 8, 12);
}
