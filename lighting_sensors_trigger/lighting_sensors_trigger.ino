
//Fill in pins 2, 3, 4, and 5 with correct pins with our arduino.
//Pins two through 10.
const red_ns = 2;
const yellow_ns = 3;
const green_ns = 4;
const blue_ns = 5;

const red_ew = 6;
const yellow_ew = 7;
const green_ew = 8;
const blue_ew = 9;


const crosswalk_border_crossed = 6;
int crosswalk_border_value = 0;


void setup() 
{
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
  digitalWrite(red_ns, HIGH);
  digitalWrite(red_ns, HIGH);
  digitalWrite(red_ns, HIGH);
  digitalWrite(red_ns, HIGH);

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
  digitalWrite(light_RED, LOW);
  //digitalWrite(light_Yellow, LOW);
  //digitalWrite(light_Green, LOW);
  //digitalWrite(light_Blue, LOW);

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
