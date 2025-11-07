#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <DHT.h>

#define DHTPIN 4
#define DHTTYPE DHT11
#define RAIN_PIN 34
#define GAS_PIN 35
#define UV_PIN 32
#define LED_DHT 14
#define LED_BMP 27
#define LED_RAIN 26
#define LED_GAS 25
#define LED_UV 33

DHT dht(DHTPIN, DHTTYPE);
Adafruit_BMP085 bmp;

bool calibrated = false;
int dryRainBaseline = 0;
int wetRainBaseline = 0;
int uvBaseline = 0;
int gasBaseline = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();

  if (!bmp.begin()) {
    Serial.println("BMP180 not detected. Check wiring!");
    while (1);
  }

  pinMode(LED_DHT, OUTPUT);
  pinMode(LED_BMP, OUTPUT);
  pinMode(LED_RAIN, OUTPUT);
  pinMode(LED_GAS, OUTPUT);
  pinMode(LED_UV, OUTPUT);

  Serial.println("Weather Station Initialized!");
  Serial.println("Calibration will run only if any sensor reports invalid data...");
}

void blinkLED(int pin) {
  digitalWrite(pin, HIGH);
  delay(100);
  digitalWrite(pin, LOW);
}

void blinkSequence() {
  blinkLED(LED_UV);
  blinkLED(LED_BMP);
  blinkLED(LED_RAIN);
  blinkLED(LED_DHT);
  blinkLED(LED_GAS);
}

void calibrateSensors() {
  Serial.println("Running sensor calibration...");
  long rainSum = 0, gasSum = 0, uvSum = 0;
  for (int i = 0; i < 10; i++) {
    rainSum += analogRead(RAIN_PIN);
    gasSum += analogRead(GAS_PIN);
    uvSum += analogRead(UV_PIN);
    delay(100);
  }
  dryRainBaseline = rainSum / 10;
  gasBaseline = gasSum / 10;
  uvBaseline = uvSum / 10;
  wetRainBaseline = dryRainBaseline - 1200; // assume ~1200 drop when wet
  wetRainBaseline = constrain(wetRainBaseline, 0, 4095);
  calibrated = true;
  Serial.println("Calibration complete.");
}

String classifyWeather(float temp, float hum, float pressure, float altitude, float rainPercent, int gasVal, int uvVal) {
  String weather = "Clear";

  if (rainPercent > 70 && hum > 80) weather = "Rain";
  else if (rainPercent > 30 && rainPercent <= 70) weather = "Drizzle";
  else if (hum > 85 && pressure < 1010) weather = "Fog";
  else if (hum > 75 && pressure < 1015) weather = "Mist";
  else if (temp <= 2 && hum > 80) weather = "Snow";
  else if (gasVal > 2000 && rainPercent > 20 && uvVal < 1500) weather = "Thunderstorm";
  else if (hum > 55 && temp < 28 && uvVal < 1800) weather = "Clouds";
  else weather = "Clear";

  return weather;
}

void loop() {
  blinkSequence();

  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  float pressure = bmp.readPressure() / 100.0;
  float altitude = bmp.readAltitude();
  int rainVal = analogRead(RAIN_PIN);
  int gasVal = analogRead(GAS_PIN);
  int uvVal = analogRead(UV_PIN);

  bool needCalib = false;
  if (isnan(temp) || isnan(hum)) needCalib = true;
  if (pressure < 800 || pressure > 1100) needCalib = true;
  if (rainVal < 10 || rainVal > 4090) needCalib = true;
  if (uvVal < 10 || uvVal > 4090) needCalib = true;

  if (!calibrated && needCalib) calibrateSensors();

  float rainPercent;
  if (calibrated)
    rainPercent = map(rainVal, wetRainBaseline, dryRainBaseline, 100, 0);
  else
    rainPercent = (4095.0 - rainVal) / 4095.0 * 100.0;

  rainPercent = constrain(rainPercent, 0.0, 100.0);

  String weather = classifyWeather(temp, hum, pressure, altitude, rainPercent, gasVal, uvVal);

  // Single clean output line
Serial.printf("Temperature: %.2f °C ", temp);
Serial.printf("Humidity: %.2f %% ", hum);
Serial.printf("Pressure: %.2f hPa ", pressure);
Serial.printf("Altitude: %.2f m ", altitude);
Serial.printf("Rain Intensity: %.2f %% ", rainPercent);
Serial.printf("Gas Level: %d ", gasVal);
Serial.printf("UV Level: %d ", uvVal);
Serial.println(weather);  // <-- single println at end for full line
Serial.println();         // blank line for spacing


  delay(3000);
}
