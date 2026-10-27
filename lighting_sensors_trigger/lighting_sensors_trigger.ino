
/*
  C.R.O.S.S. Senior Design
  Traffic Light Sequence with Ultrasonic Detection

  Original Authors: Donavin S. / Kody R.

  Changes:
  - Removed blocking traffic light delays
  - Added millis()-based traffic light control
  - Corrected 30-second detection lockout
  - Added continuous ultrasonic sensor checking
  - Prints "x" when an obstruction is detected
*/

// ======================================
// ULTRASONIC SENSOR
// ======================================

const int trigPin = 12;
const int echoPin = 11;

unsigned long duration = 0;
long cm = 0;

// Distance detection range (centimeters)
const int minDistance = 1;
const int maxDistance = 7;

// Sensor checking interval
const unsigned long sensorInterval = 100;
unsigned long lastSensorCheck = 0;

// 30-second detection lockout
const unsigned long detectionCooldown = 30000;
unsigned long detectionStart = 0;

bool sens_trig = false;


// ======================================
// TRAFFIC LIGHT PINS
// ======================================

// East-West traffic lights
const int red_ns = 2;
const int yellow_ns = 3;
const int green_ns = 4;
const int blue_ns = 5;

// North-South traffic lights
const int red_ew = 6;
const int yellow_ew = 7;
const int green_ew = 8;
const int blue_ew = 9;

// Original analog sensor input (reserved)
const int crosswalk_border_crossed = A0;


// ======================================
// TRAFFIC LIGHT TIMING
// ======================================

// Duration of each phase (milliseconds)
const unsigned long greenTime = 10000;
const unsigned long yellowTime = 5000;
const unsigned long allRedTime = 3000;

// Traffic light states
enum TrafficState
{
  EW_GREEN,
  EW_YELLOW,
  ALL_RED_NS,
  NS_GREEN,
  NS_YELLOW,
  ALL_RED_EW
};

TrafficState currentState = EW_GREEN;

unsigned long stateStartTime = 0;

// Tracks whether EW red light is active
bool redEWOn = false;


// ======================================
// SET TRAFFIC LIGHT STATE
// ======================================

void setTrafficLights(TrafficState state)
{
  // Turn all lights off first
  digitalWrite(red_ew, LOW);
  digitalWrite(yellow_ew, LOW);
  digitalWrite(green_ew, LOW);
  digitalWrite(blue_ew, LOW);

  digitalWrite(red_ns, LOW);
  digitalWrite(yellow_ns, LOW);
  digitalWrite(green_ns, LOW);
  digitalWrite(blue_ns, LOW);

  redEWOn = false;

  switch (state)
  {
    case EW_GREEN:
      digitalWrite(green_ew, HIGH);
      digitalWrite(red_ns, HIGH);
      break;

    case EW_YELLOW:
      digitalWrite(yellow_ew, HIGH);
      digitalWrite(red_ns, HIGH);
      break;

    case ALL_RED_NS:
      digitalWrite(red_ew, HIGH);
      digitalWrite(red_ns, HIGH);
      redEWOn = true;
      break;

    case NS_GREEN:
      digitalWrite(red_ew, HIGH);
      digitalWrite(green_ns, HIGH);
      redEWOn = true;
      break;

    case NS_YELLOW:
      digitalWrite(red_ew, HIGH);
      digitalWrite(yellow_ns, HIGH);
      redEWOn = true;
      break;

    case ALL_RED_EW:
      digitalWrite(red_ew, HIGH);
      digitalWrite(red_ns, HIGH);
      redEWOn = true;
      break;
  }
}


// ======================================
// UPDATE TRAFFIC LIGHTS
// ======================================

void updateTrafficLights()
{
  unsigned long currentTime = millis();
  unsigned long elapsed = currentTime - stateStartTime;

  unsigned long stateDuration = 0;

  switch (currentState)
  {
    case EW_GREEN:
    case NS_GREEN:
      stateDuration = greenTime;
      break;

    case EW_YELLOW:
    case NS_YELLOW:
      stateDuration = yellowTime;
      break;

    case ALL_RED_NS:
    case ALL_RED_EW:
      stateDuration = allRedTime;
      break;
  }

  // Move to the next light phase
  if (elapsed >= stateDuration)
  {
    switch (currentState)
    {
      case EW_GREEN:
        currentState = EW_YELLOW;
        break;

      case EW_YELLOW:
        currentState = ALL_RED_NS;
        break;

      case ALL_RED_NS:
        currentState = NS_GREEN;
        break;

      case NS_GREEN:
        currentState = NS_YELLOW;
        break;

      case NS_YELLOW:
        currentState = ALL_RED_EW;
        break;

      case ALL_RED_EW:
        currentState = EW_GREEN;
        break;
    }

    stateStartTime = currentTime;
    setTrafficLights(currentState);
  }
}


// ======================================
// ULTRASONIC SENSOR CHECK
// ======================================

void checkSensor()
{
  unsigned long currentTime = millis();

  // Allow another detection after 30 seconds
  if (sens_trig &&
      currentTime - detectionStart >= detectionCooldown)
  {
    sens_trig = false;
  }

  // Check sensor approximately every 100 ms
  if (currentTime - lastSensorCheck < sensorInterval)
  {
    return;
  }

  lastSensorCheck = currentTime;

  // Only detect while EW red light is on
  if (!redEWOn)
  {
    return;
  }

  // Send ultrasonic trigger pulse
  digitalWrite(trigPin, LOW);
  delayMicroseconds(5);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);

  digitalWrite(trigPin, LOW);

  // Read echo with a 25 ms timeout
  duration = pulseIn(echoPin, HIGH, 25000UL);

  // Ignore missing echoes
  if (duration == 0)
  {
    return;
  }

  // Convert echo time to centimeters
  cm = duration / 58;

  // Check whether a car is detected
  bool carDetected =
      (cm >= minDistance && cm <= maxDistance) ||
      (cm == 888);

  // Print x once, then start the cooldown
  if (carDetected && !sens_trig)
  {
    Serial.println("x");

    detectionStart = millis();
    sens_trig = true;
  }
}


// ======================================
// SETUP
// ======================================

void setup()
{
  // Ultrasonic sensor
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  digitalWrite(trigPin, LOW);

  // East-West LEDs
  pinMode(red_ew, OUTPUT);
  pinMode(yellow_ew, OUTPUT);
  pinMode(green_ew, OUTPUT);
  pinMode(blue_ew, OUTPUT);

  // North-South LEDs
  pinMode(red_ns, OUTPUT);
  pinMode(yellow_ns, OUTPUT);
  pinMode(green_ns, OUTPUT);
  pinMode(blue_ns, OUTPUT);

  // Analog sensor
  pinMode(crosswalk_border_crossed, INPUT);

  // Serial communication
  Serial.begin(9600);

  // Initialize traffic lights
  currentState = EW_GREEN;
  stateStartTime = millis();

  setTrafficLights(currentState);
}


// ======================================
// MAIN LOOP
// ======================================

void loop()
{
  // Keep traffic lights running
  updateTrafficLights();

  // Continuously check for obstruction
  checkSensor();
}