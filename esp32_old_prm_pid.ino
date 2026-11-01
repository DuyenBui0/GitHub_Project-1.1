
#include <Arduino.h>
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <math.h>

// =====================================================
// PIN CONFIGURATION
// =====================================================

const int adcPins[5] = {32, 33, 34, 35, 36};

#define DHT_PIN          23
#define DHT_TYPE         DHT22

#define I2C_SDA          21
#define I2C_SCL          22
#define LCD_ADDRESS      0x27

#define BUTTON_PIN       19
#define LED_PIN          18

#define MOTOR_SENSOR_PIN 27

#define NTC_ADC_PIN      39
#define HEATER_PIN       25

// =====================================================
// NTC CONFIGURATION
// =====================================================

// NTC 10K B3950
#define NTC_R0           10000.0
#define NTC_BETA         3950.0
#define NTC_T0           298.15

// Fixed resistor 10K
#define NTC_R_FIXED      10000.0

// Voltage divider supply
#define NTC_VCC_MV       3300.0

// =====================================================
// PID CONFIGURATION
// =====================================================

float SETPOINT = 80.0;

float Kp = 5.0;
float Ki = 0.05;
float Kd = 0.0;

const float MAX_SAFE_TEMP = 90.0;

const unsigned long PID_INTERVAL = 500;
const unsigned long HEATER_WINDOW = 1000;

// =====================================================
// RPM CONFIGURATION
// =====================================================

#define PULSES_PER_REV 4

const unsigned long RPM_INTERVAL = 1000;

volatile uint32_t pulseCount = 0;

portMUX_TYPE rpmMux = portMUX_INITIALIZER_UNLOCKED;

// =====================================================
// TIMING
// =====================================================

const unsigned long ADC_INTERVAL = 100;
const unsigned long DHT_INTERVAL = 2000;
const unsigned long LCD_INTERVAL = 3000;

const unsigned long DEBOUNCE_TIME = 30;

// =====================================================
// OBJECTS
// =====================================================

LiquidCrystal_I2C lcd(LCD_ADDRESS, 16, 2);
DHT dht(DHT_PIN, DHT_TYPE);

// =====================================================
// SHARED DATA
// =====================================================

int adcValue[5] = {0, 0, 0, 0, 0};

float temperature = 0.0;
float humidity = 0.0;

float ntcTemperature = NAN;

bool ntcValid = false;

float motorRPM = 0.0;

float heaterOutput = 0.0;

bool heaterFault = false;

int lcdPage = 0;

volatile int ledMode = 0;

// =====================================================
// FREE RTOS
// =====================================================

TaskHandle_t ADC_Task_Handle = NULL;
TaskHandle_t DHT_Task_Handle = NULL;
TaskHandle_t LCD_Task_Handle = NULL;
TaskHandle_t BUTTON_Task_Handle = NULL;
TaskHandle_t LED_Task_Handle = NULL;
TaskHandle_t RPM_Task_Handle = NULL;
TaskHandle_t PID_Task_Handle = NULL;

SemaphoreHandle_t serialMutex;
SemaphoreHandle_t dataMutex;

// =====================================================
// RPM INTERRUPT
// =====================================================

void IRAM_ATTR MotorSensor_ISR()
{
    portENTER_CRITICAL_ISR(&rpmMux);

    pulseCount++;

    portEXIT_CRITICAL_ISR(&rpmMux);
}

// =====================================================
// NTC TEMPERATURE READING
// =====================================================

float readNTCTemperature()
{
    uint32_t sum = 0;

    const int samples = 8;

    for (int i = 0; i < samples; i++)
    {
        sum += analogReadMilliVolts(NTC_ADC_PIN);
        delayMicroseconds(500);
    }

    float voltage = sum / (float)samples;

    // Detect open circuit / short circuit
    if (voltage < 50 || voltage > 3250)
    {
        return NAN;
    }

    // Fixed resistor connected to 3.3V
    // NTC connected to GND

    float resistance =
        NTC_R_FIXED *
        (NTC_VCC_MV - voltage) / voltage;

    if (resistance <= 0)
    {
        return NAN;
    }

    float temperatureK =
        1.0 /
        (
            (1.0 / NTC_T0) +
            (log(resistance / NTC_R0) / NTC_BETA)
        );

    float result = temperatureK - 273.15;

    if (isnan(result) || isinf(result))
    {
        return NAN;
    }

    return result;
}

// =====================================================
// ADC TASK
// =====================================================

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

            // Read 5 analog channels
            for (int i = 0; i < 5; i++)
            {
                uint32_t sum = 0;

                for (int j = 0; j < 8; j++)
                {
                    sum += analogRead(adcPins[i]);
                    delayMicroseconds(200);
                }

                tempADC[i] = sum / 8;

                // Small noise filter only
                if (tempADC[i] < 10)
                {
                    tempADC[i] = 0;
                }
            }

            // Read NTC
            float tempNTC = readNTCTemperature();

            if (xSemaphoreTake(dataMutex, pdMS_TO_TICKS(20)) == pdTRUE)
            {
                for (int i = 0; i < 5; i++)
                {
                    adcValue[i] = tempADC[i];
                }

                ntcTemperature = tempNTC;
                ntcValid = !isnan(tempNTC);

                xSemaphoreGive(dataMutex);
            }
        }

        vTaskDelay(pdMS_TO_TICKS(1));
    }
}

// =====================================================
// DHT TASK
// =====================================================

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

// =====================================================
// RPM TASK
// =====================================================

void RPM_Task(void *parameter)
{
    unsigned long previousMillis = millis();

    while (true)
    {
        unsigned long currentMillis = millis();

        if (currentMillis - previousMillis >= RPM_INTERVAL)
        {
            uint32_t pulses;

            portENTER_CRITICAL(&rpmMux);

            pulses = pulseCount;
            pulseCount = 0;

            portEXIT_CRITICAL(&rpmMux);

            float elapsed =
                (currentMillis - previousMillis) / 1000.0;

            float rpm =
                (pulses * 60.0) /
                (PULSES_PER_REV * elapsed);

            previousMillis = currentMillis;

            if (xSemaphoreTake(dataMutex, pdMS_TO_TICKS(20)) == pdTRUE)
            {
                motorRPM = rpm;

                xSemaphoreGive(dataMutex);
            }
        }

        vTaskDelay(pdMS_TO_TICKS(5));
    }
}

// =====================================================
// PID TASK
// =====================================================

void PID_Task(void *parameter)
{
    unsigned long previousMillis = millis();

    unsigned long windowStart = millis();

    float integral = 0;

    float previousTemp = 0;

    bool firstRun = true;

    float output = 0;

    while (true)
    {
        unsigned long now = millis();

        // ---------------------------------------------
        // PID CALCULATION
        // ---------------------------------------------

        if (now - previousMillis >= PID_INTERVAL)
        {
            float actualTemp;
            bool valid;

            if (xSemaphoreTake(dataMutex, pdMS_TO_TICKS(20)) == pdTRUE)
            {
                actualTemp = ntcTemperature;
                valid = ntcValid;

                xSemaphoreGive(dataMutex);
            }
            else
            {
                valid = false;
                actualTemp = NAN;
            }

            float dt =
                (now - previousMillis) / 1000.0;

            previousMillis = now;

            if (!valid || isnan(actualTemp) ||
                actualTemp >= MAX_SAFE_TEMP)
            {
                // Safety shutdown
                output = 0;

                integral = 0;

                firstRun = true;

                if (xSemaphoreTake(dataMutex, pdMS_TO_TICKS(20)) == pdTRUE)
                {
                    heaterOutput = 0;
                    heaterFault = true;

                    xSemaphoreGive(dataMutex);
                }
            }
            else
            {
                float error = SETPOINT - actualTemp;

                float proportional = Kp * error;

                float derivative = 0;

                // Derivative on measurement
                if (!firstRun && dt > 0)
                {
                    derivative =
                        -Kd * (actualTemp - previousTemp) / dt;
                }

                float integralCandidate =
                    integral + error * dt;

                float rawOutput =
                    proportional +
                    Ki * integralCandidate +
                    derivative;

                // Anti-windup
                if (!((rawOutput > 100 && error > 0) ||
                      (rawOutput < 0 && error < 0)))
                {
                    integral = integralCandidate;
                }

                integral = constrain(integral, -1000.0, 1000.0);

                output = constrain(
                    proportional +
                    Ki * integral +
                    derivative,
                    0.0,
                    100.0
                );

                previousTemp = actualTemp;

                firstRun = false;

                if (xSemaphoreTake(dataMutex, pdMS_TO_TICKS(20)) == pdTRUE)
                {
                    heaterOutput = output;
                    heaterFault = false;

                    xSemaphoreGive(dataMutex);
                }
            }
        }

        // ---------------------------------------------
        // TIME PROPORTIONAL HEATER CONTROL
        // ---------------------------------------------

        float duty;
        bool valid;
        float actualTemp;

        if (xSemaphoreTake(dataMutex, pdMS_TO_TICKS(20)) == pdTRUE)
        {
            duty = heaterOutput;
            valid = ntcValid;
            actualTemp = ntcTemperature;

            xSemaphoreGive(dataMutex);
        }
        else
        {
            duty = 0;
            valid = false;
            actualTemp = NAN;
        }

        // Independent safety check
        if (!valid || isnan(actualTemp) ||
            actualTemp >= MAX_SAFE_TEMP)
        {
            digitalWrite(HEATER_PIN, LOW);
        }
        else
        {
            if (now - windowStart >= HEATER_WINDOW)
            {
                windowStart += HEATER_WINDOW;

                if (now - windowStart >= HEATER_WINDOW)
                {
                    windowStart = now;
                }
            }

            unsigned long onTime =
                (unsigned long)(HEATER_WINDOW * duty / 100.0);

            if ((now - windowStart) < onTime)
            {
                digitalWrite(HEATER_PIN, HIGH);
            }
            else
            {
                digitalWrite(HEATER_PIN, LOW);
            }
        }

        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

// =====================================================
// LCD FUNCTIONS
// =====================================================

void lcdClearLine(uint8_t row)
{
    lcd.setCursor(0, row);
    lcd.print("                ");
    lcd.setCursor(0, row);
}

// =====================================================
// LCD TASK
// =====================================================

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
            float rpm;
            float ntc;
            float output;

            bool fault;
            bool valid;

            if (xSemaphoreTake(dataMutex, pdMS_TO_TICKS(20)) == pdTRUE)
            {
                for (int i = 0; i < 5; i++)
                {
                    adc[i] = adcValue[i];
                }

                temp = temperature;
                hum = humidity;
                rpm = motorRPM;
                ntc = ntcTemperature;
                output = heaterOutput;

                fault = heaterFault;
                valid = ntcValid;

                xSemaphoreGive(dataMutex);
            }

            // PAGE 0: ADC 32, 33
            if (lcdPage == 0)
            {
                lcdClearLine(0);
                lcd.print("A32:");
                lcd.print(adc[0]);
                lcd.print(" A33:");
                lcd.print(adc[1]);

                lcdClearLine(1);
                lcd.print("ADC MONITOR");
            }

            // PAGE 1: ADC 34, 35
            else if (lcdPage == 1)
            {
                lcdClearLine(0);
                lcd.print("A34:");
                lcd.print(adc[2]);

                lcd.print(" A35:");
                lcd.print(adc[3]);

                lcdClearLine(1);
                lcd.print("ADC MONITOR");
            }

            // PAGE 2: ADC 36 and DHT
            else if (lcdPage == 2)
            {
                lcdClearLine(0);
                lcd.print("A36:");
                lcd.print(adc[4]);

                lcdClearLine(1);
                lcd.print("DHT:");
                lcd.print(temp, 1);
                lcd.print("C");
            }

            // PAGE 3: HUMIDITY
            else if (lcdPage == 3)
            {
                lcdClearLine(0);
                lcd.print("DHT22 DATA");

                lcdClearLine(1);
                lcd.print("Hum:");
                lcd.print(hum, 1);
                lcd.print("%");
            }

            // PAGE 4: RPM
            else if (lcdPage == 4)
            {
                lcdClearLine(0);
                lcd.print("MOTOR SPEED");

                lcdClearLine(1);
                lcd.print("RPM:");
                lcd.print(rpm, 0);
            }

            // PAGE 5: PID HEATER
            else if (lcdPage == 5)
            {
                lcdClearLine(0);
                lcd.print("SET:");
                lcd.print(SETPOINT, 1);
                lcd.print("C");

                lcdClearLine(1);

                if (!valid || fault)
                {
                    lcd.print("NTC ERROR!");
                }
                else if (ntc >= MAX_SAFE_TEMP)
                {
                    lcd.print("OVER TEMP!");
                }
                else
                {
                    lcd.print("PV:");
                    lcd.print(ntc, 1);
                    lcd.print(" ");

                    lcd.print(output, 0);
                    lcd.print("%");
                }
            }

            lcdPage++;

            if (lcdPage >= 6)
            {
                lcdPage = 0;
            }
        }

        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

// =====================================================
// BUTTON TASK
// =====================================================

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

                    if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(50)) == pdTRUE)
                    {
                        Serial.print("BUTTON MODE: ");
                        Serial.println(ledMode);

                        xSemaphoreGive(serialMutex);
                    }
                }
            }
        }

        vTaskDelay(pdMS_TO_TICKS(5));
    }
}

// =====================================================
// LED TASK
// =====================================================

void LED_Task(void *parameter)
{
    bool ledState = LOW;

    unsigned long previousMillis = 0;

    while (true)
    {
        int mode = ledMode;

        if (mode == 1 || mode == 2)
        {
            unsigned long interval =
                (mode == 1) ? 500 : 1000;

            unsigned long currentMillis = millis();

            if (currentMillis - previousMillis >= interval)
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

// =====================================================
// SETUP
// =====================================================

void setup()
{
    Serial.begin(115200);

    // Force heater OFF immediately
    digitalWrite(HEATER_PIN, LOW);
    pinMode(HEATER_PIN, OUTPUT);
    digitalWrite(HEATER_PIN, LOW);

    pinMode(MOTOR_SENSOR_PIN, INPUT);

    pinMode(BUTTON_PIN, INPUT);

    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);

    // ADC
    analogReadResolution(12);
    analogSetPinAttenuation(NTC_ADC_PIN, ADC_11db);

    for (int i = 0; i < 5; i++)
    {
        pinMode(adcPins[i], INPUT);
    }

    pinMode(NTC_ADC_PIN, INPUT);

    // Interrupt
    attachInterrupt(
        digitalPinToInterrupt(MOTOR_SENSOR_PIN),
        MotorSensor_ISR,
        RISING
    );

    // DHT
    dht.begin();

    // LCD
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

    // Mutex
    serialMutex = xSemaphoreCreateMutex();
    dataMutex = xSemaphoreCreateMutex();

    if (serialMutex == NULL || dataMutex == NULL)
    {
        digitalWrite(HEATER_PIN, LOW);

        while (true)
        {
            delay(1000);
        }
    }

    // ADC TASK
    xTaskCreatePinnedToCore(
        ADC_Task, "ADC_Task",
        4096, NULL, 2,
        &ADC_Task_Handle, 0
    );

    // DHT TASK
    xTaskCreatePinnedToCore(
        DHT_Task, "DHT_Task",
        4096, NULL, 1,
        &DHT_Task_Handle, 1
    );

    // LCD TASK
    xTaskCreatePinnedToCore(
        LCD_Task, "LCD_Task",
        4096, NULL, 1,
        &LCD_Task_Handle, 1
    );

    // BUTTON TASK
    xTaskCreatePinnedToCore(
        BUTTON_Task, "BUTTON_Task",
        2048, NULL, 2,
        &BUTTON_Task_Handle, 1
    );

    // LED TASK
    xTaskCreatePinnedToCore(
        LED_Task, "LED_Task",
        2048, NULL, 1,
        &LED_Task_Handle, 1
    );

    // RPM TASK
    xTaskCreatePinnedToCore(
        RPM_Task, "RPM_Task",
        2048, NULL, 2,
        &RPM_Task_Handle, 0
    );

    // PID TASK
    xTaskCreatePinnedToCore(
        PID_Task, "PID_Task",
        4096, NULL, 2,
        &PID_Task_Handle, 1
    );
}

// =====================================================
// LOOP
// =====================================================

void loop()
{
    vTaskDelay(pdMS_TO_TICKS(1000));
}
