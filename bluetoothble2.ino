#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

// Define the UUIDs for the service and characteristic
#define SERVICE_UUID "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID_timer "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define CHARACTERISTIC_UUID_status "c9180a0c-c4d6-4734-8bb7-00b001bb4f66"

// Define the Bluetooth server and characteristic objects
BLEServer* pServer = NULL;
BLECharacteristic* pCharacteristic_timer = NULL;
BLEService* pService = NULL;

// bool gameStart = true;


// Define the sensor pin
const int sensorPin = 34;
int passcount = 0;

void setup() {
  Serial.begin(115200);
  // Create the BLE device
  BLEDevice::init("ESP32 Sensor");

  // Create the BLE server
  pServer = BLEDevice::createServer();

  // Create the BLE service
  BLEService* pService = pServer->createService(SERVICE_UUID);

  // Create the BLE characteristic
  pCharacteristic_timer = pService->createCharacteristic(
    CHARACTERISTIC_UUID_timer,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_WRITE);
  

  // Start the BLE service
  pService->start();

  // Start advertising the BLE service
  BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(pService->getUUID());
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);
  pAdvertising->setMinPreferred(0x12);
  BLEDevice::startAdvertising();
}


void loop() {
  // Read the sensor data
  // int sensorValue = analogRead(sensorPin);
  std::string ReadValue = pCharacteristic_timer->getValue();
  if (ReadValue == "gameStart") {
    if (analogRead(sensorPin) > 2500) {
      unsigned long startTime = millis();
      Serial.print("starttime: ");
      Serial.println(startTime);
      unsigned long currentTime;
      while (analogRead(sensorPin) > 2500) {
        currentTime = millis() - startTime;
        Serial.print("current time: ");
        Serial.println(currentTime);
        passcount++;                       //dit is de counter
        Serial.println(passcount);
        if(passcount > 0){                 // pas hier de snelheid aan. hoger is langer wachten met updaten
          std::string message = std::to_string(currentTime);
          std::string addTimer = ";timer loopt";
          message = message + addTimer;
          pCharacteristic_timer->setValue(message);
          pCharacteristic_timer->notify();
          passcount = 0;
        }
        delay(5);
      }
    std::string message = std::to_string(currentTime);
    std::string addTimer = ";stop timer";
    message = message + addTimer;
    pCharacteristic_timer->setValue(message);
    pCharacteristic_timer->notify();
    delay(600);
    message = "stop timer";
    // gameStart = false;
    delay(200);
    // break;
    }
    Serial.println("ESP ready");
  }
  if (ReadValue == "DISCONNECT") {
    BLEDevice::getAdvertising()->stop();
    Serial.println("Disconnected");

    pServer->removeService(pService); // Remove the service
    BLEDevice::deinit(); // Deinitialize BLE

    delay(2000);
    BLEDevice::init("ESP32 Sensor"); // Reinitialize BLE
    pServer = BLEDevice::createServer();
    pService = pServer->createService(SERVICE_UUID); // Recreate the service

    pCharacteristic_timer = pService->createCharacteristic(
      CHARACTERISTIC_UUID_timer,
      BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_WRITE
    );

    pService->start();

    BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(pService->getUUID());
    pAdvertising->setScanResponse(true);
    pAdvertising->setMinPreferred(0x06);
    pAdvertising->setMinPreferred(0x12);
    BLEDevice::startAdvertising();

    Serial.println("ESP is discoverable again");
  }

  delay(100);
}