#include <EEPROM.h>

#define RELAY_D12 12
#define RELAY_D11 11
#define HEART_LED 13

// Thời gian
unsigned long startTime;
unsigned long now;
unsigned long firstPrintTime;

// ADC
int adc0 = 0;
int adc1 = 0;
int adc2 = 0;

int adc0_Max = 0;
int adc1_Max = 0;

// Giá trị cũ đọc từ EEPROM (hiển thị 5s đầu 1 lần)
int old_adc0_Max = 0;
int old_adc1_Max = 0;
unsigned int old_d12_on_minutes = 0;
bool printedOldOnce = false;

// Kiểm tra điều kiện adc cao liên tục 3s
unsigned long adcHighStart = 0;
bool adcHighTimerRunning = false;

// EEPROM protection: chỉ ghi 1 lần cho lần chạy này
bool eepromSaved = false;

// Heartbeat
unsigned long heartbeatTimer = 0;
byte heartbeatState = 0;
bool heartbeatEnabled = false;

// Theo dõi thời gian D12 ON lần này
unsigned long d12OnMillis = 0;
bool d12IsOn = false;

// Ngưỡng và khoảng thời gian
const int ADC_THRESHOLD = 520;
const unsigned long ADC_HIGH_REQUIRED_MS = 3000UL;
const unsigned long BOOT_WAIT_MS = 2000UL;
const unsigned long SHOW_OLD_WINDOW_MS = 5000UL;
const unsigned long ONE_MIN_MS = 60000UL;

// Hàm heartbeat (nhịp tim): On 80ms → Off 80ms → On 80ms → Off 600ms
void heartbeat() {
  unsigned long t = millis();
  switch (heartbeatState) {
    case 0:
      digitalWrite(HEART_LED, HIGH);
      if (t - heartbeatTimer >= 80) {
        heartbeatTimer = t;
        heartbeatState = 1;
      }
      break;
    case 1:
      digitalWrite(HEART_LED, LOW);
      if (t - heartbeatTimer >= 80) {
        heartbeatTimer = t;
        heartbeatState = 2;
      }
      break;
    case 2:
      digitalWrite(HEART_LED, HIGH);
      if (t - heartbeatTimer >= 80) {
        heartbeatTimer = t;
        heartbeatState = 3;
      }
      break;
    case 3:
      digitalWrite(HEART_LED, LOW);
      if (t - heartbeatTimer >= 600) {
        heartbeatTimer = t;
        heartbeatState = 0;
      }
      break;
  }
}

void setup() {
  Serial.begin(9600);

  pinMode(RELAY_D12, OUTPUT);
  pinMode(RELAY_D11, OUTPUT);
  pinMode(HEART_LED, OUTPUT);

  digitalWrite(RELAY_D12, LOW);
  digitalWrite(RELAY_D11, LOW);
  digitalWrite(HEART_LED, LOW);

  startTime = millis();
  firstPrintTime = startTime;

  // Đọc giá trị cũ từ EEPROM
  old_adc0_Max = (EEPROM.read(0) << 8) | EEPROM.read(1);
  old_adc1_Max = (EEPROM.read(2) << 8) | EEPROM.read(3);
  old_d12_on_minutes = (EEPROM.read(4) << 8) | EEPROM.read(5);

  // Khởi tạo các biến max hiện tại về 0 (bắt đầu ghi lại từ 0)
  adc0_Max = 0;
  adc1_Max = 0;
}

void loop() {
  now = millis();

  // 1) Chờ 2 giây khởi động (không dùng delay)
  if (now - startTime < BOOT_WAIT_MS) {
    // Trong khoảng chờ 2s vẫn in nothing (hoặc có thể in 'boot' nếu cần)
    return;
  }

  // Sau 2 giây: bật D12 và D11 (nếu chưa bật)
  if (!d12IsOn) {
    digitalWrite(RELAY_D12, HIGH);
    d12OnMillis = now;
    d12IsOn = true;
    heartbeatEnabled = true; // bật nhịp tim (D13)
  }
  // luôn bật D11 ở giai đoạn này cho tới khi adc2==0
  digitalWrite(RELAY_D11, HIGH);

  // Heartbeat nếu enabled
  if (heartbeatEnabled) heartbeat();

  // 2) Đọc ADC liên tục
  adc0 = analogRead(A0);
  adc1 = analogRead(A1);
  adc2 = analogRead(A2);

  // Luôn cập nhật max hiện tại
  if (adc0 > adc0_Max) adc0_Max = adc0;
  if (adc1 > adc1_Max) adc1_Max = adc1;

  // 3) Kiểm tra điều kiện tắt D12 + D13:
  // adc0 > 520 OR adc1 > 520 liên tục trong 3 giây
  if (adc0 > ADC_THRESHOLD || adc1 > ADC_THRESHOLD) {
    if (!adcHighTimerRunning) {
      adcHighTimerRunning = true;
      adcHighStart = now;
    }
  } else {
    // nếu giá trị rớt xuống thì reset bộ đếm
    adcHighTimerRunning = false;
  }

  if (adcHighTimerRunning && !eepromSaved) {
    if (now - adcHighStart >= ADC_HIGH_REQUIRED_MS) {
      // Dừng D12 và D13
      digitalWrite(RELAY_D12, LOW);
      d12IsOn = false;
      heartbeatEnabled = false;
      digitalWrite(HEART_LED, LOW);

      // Tính thời gian ON của D12 tính bằng phút
      unsigned long d12DurationMs = now - d12OnMillis;
      unsigned int d12Minutes = (unsigned int)(d12DurationMs / ONE_MIN_MS); // số phút (làm tròn xuống)

      // Ghi vào EEPROM (2 byte cho adc0_Max, 2 byte cho adc1_Max, 2 byte cho d12Minutes)
      int a0 = adc0_Max;
      int a1 = adc1_Max;
      unsigned int m = d12Minutes;

      EEPROM.update(0, highByte(a0));
      EEPROM.update(1, lowByte(a0));
      EEPROM.update(2, highByte(a1));
      EEPROM.update(3, lowByte(a1));
      EEPROM.update(4, highByte(m));
      EEPROM.update(5, lowByte(m));

      eepromSaved = true;

      Serial.println(">>> D12 turned OFF - EEPROM saved (adc0_Max, adc1_Max, d12_minutes)");
      Serial.print("Saved adc0_Max="); Serial.print(a0);
      Serial.print("  adc1_Max="); Serial.print(a1);
      Serial.print("  d12_minutes="); Serial.println(m);
    }
  }

  // 4) D11 chạy tới khi ADC2 == 0 -> tắt ngay
  if (adc2 == 0) {
    digitalWrite(RELAY_D11, LOW);
  }

  // 5) In dữ liệu Serial:
  // - Trong 5s đầu: in 1 lần giá trị cũ (EEPROM) + vẫn in adc hiện tại
  // - Sau 5s: in adc hiện tại và max hiện tại (không in giá trị cũ nữa)
  // Lưu ý: in giá trị cũ **chỉ 1 lần** trong khoảng 5s đầu
  if ((now - firstPrintTime) <= SHOW_OLD_WINDOW_MS) {
    // 5s đầu
    if (!printedOldOnce) {
      Serial.println("=== BOOT-INFO (OLD from EEPROM) ===");
      Serial.print("old_adc0_Max = "); Serial.println(old_adc0_Max);
      Serial.print("old_adc1_Max = "); Serial.println(old_adc1_Max);
      Serial.print("old_D12_on_minutes = "); Serial.println(old_d12_on_minutes);
      Serial.println("===================================");
      printedOldOnce = true;
    }

    // vẫn in các ADC hiện tại + max hiện tại
    Serial.print("[BOOT] adc0="); Serial.print(adc0);
    Serial.print("  adc1="); Serial.print(adc1);
    Serial.print("  adc2="); Serial.print(adc2);
    Serial.print("  => maxNow A0="); Serial.print(adc0_Max);
    Serial.print("  A1="); Serial.println(adc1_Max);
  } else {
    // sau 5s
    Serial.print("adc0="); Serial.print(adc0);
    Serial.print("  adc1="); Serial.print(adc1);
    Serial.print("  adc2="); Serial.print(adc2);
    Serial.print("  => maxNow A0="); Serial.print(adc0_Max);
    Serial.print("  A1="); Serial.println(adc1_Max);
  }

  // Lưu ý: vòng loop chạy nhanh; nếu muốn giảm tốc in serial có thể thêm một cơ chế in theo interval
  // (ví dụ in mỗi 200ms). Hiện để đơn giản in mỗi vòng.
}
