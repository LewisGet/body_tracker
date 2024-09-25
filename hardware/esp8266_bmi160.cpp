#include <Wire.h>
#include <BMI160Gen.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <TimeLib.h>

const int i2c_addr_1 = 0x68;  // BMI160 I2C 地址
const int i2c_addr_2 = 0x69;  // BMI160 I2C 地址

BMI160GenClass BMI160_1;  // 第一個感測器
// BMI160GenClass BMI160_2; // 第二個感測器

#define D4_PIN 0  // D4 對應 GPIO0
#define D3_PIN 2  // D3 對應 GPIO2

#define D2_PIN 4  // D2 對應 GPIO4
#define D1_PIN 5  // D1 對應 GPIO5

const char *ssid = "lewis-wifi";
const char *password = "password";

WiFiUDP ntpUDP;
ESP8266WiFiClass Wifi;

const char* ntpServer = "pool.ntp.org";
// const long gmtOffset_sec = 28800; // +8 utm
const long gmtOffset_sec = 0;

NTPClient timeClient(ntpUDP, ntpServer, gmtOffset_sec, 60000);  // 更新間隔為 60 秒

WiFiClientSecure client;
String request_host = "http://192.168.100.100:8000";

int targetPartsId = 1;
int targetPartsType = 0;

unsigned int cacheIndex = 0;
unsigned int pushIndex = 0;
unsigned int dataPushStep = 100;
unsigned int dataSize = 40 * 5; // 40 fps，五秒 upload 一次
float cacheX[200];
float cacheY[200];
float cacheZ[200];
unsigned long long cacheTime[200];


float convertRawGyro(int gRaw) {
  // since we are using 250 degrees/seconds range
  // -250 maps to a raw value of -32768
  // +250 maps to a raw value of 32767

  float g = (gRaw * 250.0) / 32768.0;

  return g;
}

void initWIFI() {
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  Serial.print("connect wifi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
}

void connectNTP() {
  timeClient.begin();
  timeClient.update();
}

void initBMI() {
  Serial.println("BMI160 initialization");
  if (!BMI160_1.begin(BMI160GenClass::I2C_MODE, i2c_addr_2)) {
    Serial.println("failed");
    delay(500);
    return;
  }

  Serial.println("BMI160 initialization succeeded");
}

unsigned long long getTimestamp() {
  unsigned long now = timeClient.getEpochTime();

  int currentYear = year(now);
  int currentMonth = month(now);
  int currentDay = day(now);
  int currentHour = hour(now);
  int currentMinute = minute(now);
  int currentSecond = second(now);

  struct tm t;
  t.tm_year = currentYear - 1900;
  t.tm_mon = currentMonth - 1;
  t.tm_mday = currentDay;
  t.tm_hour = currentHour;
  t.tm_min = currentMinute;
  t.tm_sec = currentSecond;
  t.tm_isdst = -1; // 自動判斷是否為夏令時

  unsigned long long currentMillis = mktime(&t);

  currentMillis = currentMillis * 1000 + (millis() % 1000);

  return currentMillis;
}

void read_bmi(BMI160GenClass BMI160, float& x, float& y, float& z) {
  int axRaw, ayRaw, azRaw;
  float ax, ay, az;
  int gxRaw, gyRaw, gzRaw;
  float gx, gy, gz;

  // 讀取加速度計數據
  BMI160.readAccelerometer(axRaw, ayRaw, azRaw);
  // 讀取陀螺儀數據
  BMI160.readGyro(gxRaw, gyRaw, gzRaw);

  ax = convertRawGyro(axRaw);
  ay = convertRawGyro(ayRaw);
  az = convertRawGyro(azRaw);

  gx = convertRawGyro(gxRaw);
  gy = convertRawGyro(gyRaw);
  gz = convertRawGyro(gzRaw);

  x = atan2(ay, az) * 180 / PI;
  y = atan2(ax, az) * 180 / PI;
  z = atan2(ax, ay) * 180 / PI;
}

HTTPClient httpGetRequest(String url) {
  HTTPClient http;
  WiFiClient client;

  if (WiFi.status() == WL_CONNECTED) {
    http.begin(client, url); // 指定 URL

    int httpCode = http.GET(); // 執行 GET 請求

    if (httpCode > 0) { // 檢查 HTTP 回應碼
      String payload = http.getString(); // 獲取回應內容
      Serial.println(payload);
    } else {
      Serial.printf("GET request failed, error: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end(); // 關閉連接
  } else {
    Serial.println("WiFi not connected");
  }

  return http;
}

HTTPClient httpPostRequest(String url, String payload) {
  HTTPClient http;
  WiFiClient client;

  if (WiFi.status() == WL_CONNECTED) {
    http.begin(client, url);
    http.addHeader("Content-Type", "application/json");

    int httpCode = http.POST(payload); // 執行 POST 請求

    if (httpCode > 0) { // 檢查 HTTP 回應碼
      String payload = http.getString(); // 獲取回應內容
      Serial.println(payload);
    } else {
      Serial.printf("GET request failed, error: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end(); // 關閉連接
  } else {
    Serial.println("WiFi not connected");
  }

  return http;
}

String floatJoinValue(float* value) {
  String returnValue = "";

  for (int i = 0; i < dataSize; i++)
  {
    if (returnValue == "")
    {
      returnValue = String(value[i]);
    }
    else
    {
      returnValue = returnValue + "," + String(value[i]);
    }
  }

  return returnValue;
}

String timeJoinValue(unsigned long long* value) {
  String returnValue = "";

  for (int i = 0; i < dataSize; i++)
  {
    if (returnValue == "")
    {
      returnValue = String(value[i]);
    }
    else
    {
      returnValue = returnValue + "," + String(value[i]);
    }
  }

  return returnValue;
}

String fiexIntJoinValue(int value) {
  String returnValue = "";

  for (int i = 0; i < dataSize; i++)
  {
    if (returnValue == "")
    {
      returnValue = String(value);
    }
    else
    {
      returnValue = returnValue + "," + String(value);
    }
  }

  return returnValue;
}

String dataToUri() {
  String uri = "";
  String xs = "";
  String ys = "";
  String zs = "";
  String times = "";
  // String targetIds = "";
  // String targetTypes = "";

  xs = floatJoinValue(cacheX);
  ys = floatJoinValue(cacheY);
  zs = floatJoinValue(cacheZ);
  times = timeJoinValue(cacheTime);
  // targetIds = fiexIntJoinValue(targetPartsId);
  // targetTypes = fiexIntJoinValue(targetPartsType);

  uri = "/record/api/batch/create/action_log/?x=" + xs + "&y=" + ys + "&z=" + zs + "&timestamp=" + times + "&target_id=" + targetPartsId + "&target_type=" + targetPartsType;

  return uri;
}

String dataToJson() {
  String payload = "";
  String xs = "";
  String ys = "";
  String zs = "";
  String times = "";
  // String targetIds = "";
  // String targetTypes = "";

  xs = floatJoinValue(cacheX);
  ys = floatJoinValue(cacheY);
  zs = floatJoinValue(cacheZ);
  times = timeJoinValue(cacheTime);
  // targetIds = fiexIntJoinValue(targetPartsId);
  // targetTypes = fiexIntJoinValue(targetPartsType);

  payload = "{";
    payload += "\"x\": \"" + String(xs) + "\",";
    payload += "\"y\": \"" + String(ys) + "\",";
    payload += "\"z\": \"" + String(zs) + "\",";
    payload += "\"timestamp\": \"" + String(times) + "\",";
    payload += "\"target_id\": \"" + String(targetPartsId) + "\",";
    payload += "\"target_type\": \"" + String(targetPartsType) + "\"";
  payload += "}";

  return payload;
}

void initRequestHost() {
  IPAddress ip = Wifi.localIP();

  for (int i = 0; i < 255; i++)
  {
    ip[3] = i;

    String search_ip = ip.toString();
    HTTPClient http = httpGetRequest("http://" + search_ip + ":8000/record/api/scan/location");
    Serial.println("search ip: " + search_ip);

    if (http.GET() == 200)
    {
      request_host = "http://" + search_ip + ":8000";
      Serial.println("host found: " + request_host);
      return;
    }
  }

  Serial.println("host not found.");
  return;
}

void initCache() {
  for (int i = 0; i < dataSize; i++)
  {
    cacheX[cacheIndex] = 0;
    cacheY[cacheIndex] = 0;
    cacheZ[cacheIndex] = 0;
    cacheTime[cacheIndex] = 0;
  }
}

void setup() {
  Serial.begin(115200);
  Wire.begin(D1_PIN, D2_PIN);  // SDA, SCL

  initWIFI();
  connectNTP();
  initBMI();
  initCache();
  initRequestHost();
}

void loop() {
  float gx, gy, gz;
  read_bmi(BMI160_1, gx, gy, gz);

  cacheX[cacheIndex] = gx;
  cacheY[cacheIndex] = gy;
  cacheZ[cacheIndex] = gz;
  cacheTime[cacheIndex] = getTimestamp();

  cacheIndex = cacheIndex + 1;
  pushIndex = pushIndex + 1;

  if (cacheIndex >= dataSize)
  {
    cacheIndex = 0;
  }

  if (pushIndex >= dataPushStep)
  {
    pushIndex = 0;
    String url = request_host + "/record/api/batch/create/action_log/";
    httpPostRequest(url, dataToJson());
  }

  delay(25);
}
