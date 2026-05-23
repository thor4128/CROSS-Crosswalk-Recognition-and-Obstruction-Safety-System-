//Author: Donavin S.
//Reviewer: Kody R.
//Senior Design
//Traffic Pattern LEDs with Sensor for Motion Detection

//Fill in pins 2, 3, 4, 5, 6, 7, 8, and 9 with correct pins with our arduino.
#include "Arduino_LED_Matrix.h"

ArduinoLEDMatrix matrix;

//Street facing north and south uses 4 lights, with pins 2 through 5.
const int red_ns = 2;
const int yellow_ns = 3;
const int green_ns = 4;
const int blue_ns = 5;

//Street facing east and west uses 4 lights, with pins, 6 through 9.
const int red_ew = 6;
const int yellow_ew = 7;
const int green_ew = 8;
const int blue_ew = 9;

//Variables for motion sensor detection.
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
  //These are the LEDs for the North and South Traffic Light.
  pinMode(red_ns, OUTPUT);
  pinMode(yellow_ns, OUTPUT);
  pinMode(green_ns, OUTPUT);
  pinMode(blue_ns, OUTPUT);

  //Initialize lights as outputs.
  //These are the LEDs for the East and West Traffic Light.
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

  crosswalk_border_value = analogRead(crosswalk_border_crossed);
  
  //Lights turn off.
  //All are off, except red LEDs.
  digitalWrite(red_ns, HIGH);
  digitalWrite(yellow_ns, LOW);
  digitalWrite(green_ns, LOW);
  digitalWrite(blue_ns, LOW);
  digitalWrite(red_ew, LOW);
  digitalWrite(yellow_ew, LOW);
  digitalWrite(green_ew, HIGH);
  digitalWrite(blue_ew, LOW);
  
 //red_ns LED stays HIGH for 45 seconds.
 //Red light time might be 30 to 90 seconds standard intersection.
 delay(90000);
 //delay(45000);
 //delay(10000);

 /* red_ns transitions into green_ns
  * 
  * This means that after 45 seconds, green_ew turns off, because there is 6 seconds of yellow_ew on.
  * 
  * Then, once yellow_ew is done, red_ew turns on, and green_ns turns on.
  */

 //Yellow for EW turns on for 5 seconds.
 digitalWrite(green_ew, LOW);
 digitalWrite(yellow_ew, HIGH);
 delay(5000);

 digitalWrite(red_ns, HIGH);
 digitalWrite(red_ew, HIGH);
 digitalWrite(yellow_ew, LOW);

 //Delay with both lights being red, (waiting for the transition of one Green LED to turn on).
 //Waiting for the intersection to be clear.
 delay(3000);

 //Then, red_ns LED turns off, and green_ns turns on and red_ew turns on.
 //Then yellow_ew also turns off, since the next traffic pattern will occur.
 digitalWrite(red_ns, LOW);
 digitalWrite(green_ns, HIGH);
 digitalWrite(red_ew, HIGH);
 digitalWrite(yellow_ew, LOW);

 //North South Green LED stays green for 60 seconds/red_ew is HIGH for 45 seconds.
 //Red light time might be 90 seconds standard intersection.
 delay(90000);
 //delay(45000);
 //delay(10000);


//Once green_ns LED turns off, yellow_ns ON for 5 seconds.
 digitalWrite(green_ns, LOW);
 digitalWrite(yellow_ns, HIGH);
 delay(5000);

 digitalWrite(red_ns, HIGH);
 digitalWrite(red_ew, HIGH);
 digitalWrite(yellow_ns, LOW);

//Delay with both lights being red, (waiting for the transition of one Green LED to turn on).
//Waiting for the intersection to be clear.
 delay(3000);

}

void showOn()
{
  matrix.renderBitmap(onFrame, 8, 12);
}

void showOff()
{
  matrix.renderBitmap(offFrame, 8, 12);
}
