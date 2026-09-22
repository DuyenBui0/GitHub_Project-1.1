#include <Arduino.h>
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

const int adcPins[5] = {32, 33, 34, 35, 36};

#define DHT_PIN 23
#define DHT_TYPE DHT22

#define I2C_SDA 21
#define I2C_SCL 22
#define LCD_ADDRESS 0x27

#define BUTTON_PIN 19
#define LED_PIN 18

LiquidCrystal_I2C lcd(LCD_ADDRESS, 16, 2);
DHT dht(DHT_PIN, DHT_TYPE);

int adcValue[5] = {0, 0, 0, 0, 0};
float temperature = 0.0;
float humidity = 0.0;

const unsigned long ADC_INTERVAL = 100;
const unsigned long DHT_INTERVAL = 2000;
const unsigned long LCD_INTERVAL = 1000;

const unsigned long DEBOUNCE_TIME = 30;

TaskHandle_t ADC_Task_Handle = NULL;
TaskHandle_t DHT_Task_Handle = NULL;
TaskHandle_t LCD_Task_Handle = NULL;
TaskHandle_t BUTTON_Task_Handle = NULL;
TaskHandle_t LED_Task_Handle = NULL;

SemaphoreHandle_t serialMutex;
SemaphoreHandle_t dataMutex;

int lcdPage = 0;

volatile int ledMode = 0;
volatile bool buttonEvent = false;

void ADC_Task(void *parameter)
{
  unsigned long previousMillis = 0;

  while (true)
  {
    unsigned long currentMillis = millis();

    if (currentMillis - previousMillis >= ADC_INTERVAL)
    {
      previousMillis = currentMillis;

      int tempADC[5];

      for (int i = 0; i < 5; i++)
      {
        tempADC[i] = analogRead(adcPins[i]);
      }

      if (xSemaphoreTake(dataMutex, pdMS_TO_TICKS(20)) == pdTRUE)
      {
        for (int i = 0; i < 5; i++)
        {
          adcValue[i] = tempADC[i];
        }

        xSemaphoreGive(dataMutex);
      }

      int adc[5];
      float temp;
      float hum;

      if (xSemaphoreTake(dataMutex, pdMS_TO_TICKS(20)) == pdTRUE)
      {
        for (int i = 0; i < 5; i++)
        {
          adc[i] = adcValue[i];
        }

        temp = temperature;
        hum = humidity;

        xSemaphoreGive(dataMutex);
      }

      if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(50)) == pdTRUE)
      {
        Serial.print("ADC32: ");
        Serial.print(adc[0]);

        Serial.print("  ADC33: ");
        Serial.print(adc[1]);

        Serial.print("  ADC34: ");
        Serial.print(adc[2]);

        Serial.print("  ADC35: ");
        Serial.print(adc[3]);

        Serial.print("  ADC36: ");
        Serial.print(adc[4]);

        Serial.print("  TEMP: ");
        Serial.print(temp, 1);
        Serial.print(" C");

        Serial.print("  HUM: ");
        Serial.print(hum, 1);
        Serial.println(" %");

        xSemaphoreGive(serialMutex);
      }
    }

    vTaskDelay(pdMS_TO_TICKS(1));
  }
}

void DHT_Task(void *parameter)
{
  unsigned long previousMillis = 0;

  while (true)
  {
    unsigned long currentMillis = millis();

    if (currentMillis - previousMillis >= DHT_INTERVAL)
    {
      previousMillis = currentMillis;

      float h = dht.readHumidity();
      float t = dht.readTemperature();

      if (!isnan(h) && !isnan(t))
      {
        if (xSemaphoreTake(dataMutex, pdMS_TO_TICKS(20)) == pdTRUE)
        {
          humidity = h;
          temperature = t;

          xSemaphoreGive(dataMutex);
        }
      }
      else
      {
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(50)) == pdTRUE)
        {
          Serial.println("DHT22 read error");
          xSemaphoreGive(serialMutex);
        }
      }
    }

    vTaskDelay(pdMS_TO_TICKS(10));
  }
}

void lcdClearLine(uint8_t row)
{
  lcd.setCursor(0, row);
  lcd.print("                ");
  lcd.setCursor(0, row);
}

void LCD_Task(void *parameter)
{
  unsigned long previousMillis = 0;

  while (true)
  {
    unsigned long currentMillis = millis();

    if (currentMillis - previousMillis >= LCD_INTERVAL)
    {
      previousMillis = currentMillis;

      int adc[5];
      float temp;
      float hum;

      if (xSemaphoreTake(dataMutex, pdMS_TO_TICKS(20)) == pdTRUE)
      {
        for (int i = 0; i < 5; i++)
        {
          adc[i] = adcValue[i];
        }

        temp = temperature;
        hum = humidity;

        xSemaphoreGive(dataMutex);
      }

      if (lcdPage == 0)
      {
        lcdClearLine(0);
        lcd.print("A32:");
        lcd.print(adc[0]);
        lcd.print(" A33:");
        lcd.print(adc[1]);

        lcdClearLine(1);
        lcd.print("A34:");
        lcd.print(adc[2]);
        lcd.print(" A35:");
        lcd.print(adc[3]);
      }
      else if (lcdPage == 1)
      {
        lcdClearLine(0);
        lcd.print("ADC36:");
        lcd.print(adc[4]);

        lcdClearLine(1);
        lcd.print("TEMP:");
        lcd.print(temp, 1);
        lcd.print(" C");
      }
      else if (lcdPage == 2)
      {
        lcdClearLine(0);
        lcd.print("DHT22 SENSOR");

        lcdClearLine(1);
        lcd.print("HUM:");
        lcd.print(hum, 1);
        lcd.print(" %");
      }
      else if (lcdPage == 3)
      {
        lcdClearLine(0);
        lcd.print("TEMP:");
        lcd.print(temp, 1);
        lcd.print(" C");

        lcdClearLine(1);
        lcd.print("HUM:");
        lcd.print(hum, 1);
        lcd.print(" %");
      }

      lcdPage++;

      if (lcdPage >= 4)
      {
        lcdPage = 0;
      }
    }

    vTaskDelay(pdMS_TO_TICKS(10));
  }
}

void BUTTON_Task(void *parameter)
{
  bool lastRawState = LOW;
  bool stableState = LOW;

  unsigned long lastChangeTime = 0;

  while (true)
  {
    bool rawState = digitalRead(BUTTON_PIN);

    if (rawState != lastRawState)
    {
      lastChangeTime = millis();
      lastRawState = rawState;
    }

    if (millis() - lastChangeTime >= DEBOUNCE_TIME)
    {
      if (rawState != stableState)
      {
        stableState = rawState;

        if (stableState == HIGH)
        {
          ledMode++;

          if (ledMode > 3)
          {
            ledMode = 1;
          }

          if (ledMode == 1)
          {
            Serial.println("BUTTON: MODE 1 - LED 0.5s");
          }
          else if (ledMode == 2)
          {
            Serial.println("BUTTON: MODE 2 - LED 1.0s");
          }
          else if (ledMode == 3)
          {
            Serial.println("BUTTON: MODE 3 - LED OFF");
          }
        }
      }
    }

    vTaskDelay(pdMS_TO_TICKS(5));
  }
}

void LED_Task(void *parameter)
{
  bool ledState = LOW;
  unsigned long previousMillis = 0;

  while (true)
  {
    int mode = ledMode;

    if (mode == 1)
    {
      unsigned long currentMillis = millis();

      if (currentMillis - previousMillis >= 500)
      {
        previousMillis = currentMillis;

        ledState = !ledState;
        digitalWrite(LED_PIN, ledState);
      }
    }
    else if (mode == 2)
    {
      unsigned long currentMillis = millis();

      if (currentMillis - previousMillis >= 1000)
      {
        previousMillis = currentMillis;

        ledState = !ledState;
        digitalWrite(LED_PIN, ledState);
      }
    }
    else
    {
      ledState = LOW;
      digitalWrite(LED_PIN, LOW);
      previousMillis = millis();
    }

    vTaskDelay(pdMS_TO_TICKS(5));
  }
}

void setup()
{
  Serial.begin(115200);

  analogReadResolution(12);

  pinMode(BUTTON_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);

  digitalWrite(LED_PIN, LOW);

  dht.begin();

  Wire.begin(I2C_SDA, I2C_SCL);

  lcd.init();
  lcd.backlight();
  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("ESP32 MONITOR");

  lcd.setCursor(0, 1);
  lcd.print("Starting...");

  delay(1000);

  lcd.clear();

  serialMutex = xSemaphoreCreateMutex();
  dataMutex = xSemaphoreCreateMutex();

  xTaskCreatePinnedToCore(
    ADC_Task,
    "ADC_Task",
    4096,
    NULL,
    2,
    &ADC_Task_Handle,
    0
  );

  xTaskCreatePinnedToCore(
    DHT_Task,
    "DHT_Task",
    4096,
    NULL,
    1,
    &DHT_Task_Handle,
    1
  );

  xTaskCreatePinnedToCore(
    LCD_Task,
    "LCD_Task",
    4096,
    NULL,
    1,
    &LCD_Task_Handle,
    1
  );

  xTaskCreatePinnedToCore(
    BUTTON_Task,
    "BUTTON_Task",
    2048,
    NULL,
    2,
    &BUTTON_Task_Handle,
    1
  );

  xTaskCreatePinnedToCore(
    LED_Task,
    "LED_Task",
    2048,
    NULL,
    1,
    &LED_Task_Handle,
    1
  );
}

void loop()
{
  vTaskDelay(pdMS_TO_TICKS(1000));
}
