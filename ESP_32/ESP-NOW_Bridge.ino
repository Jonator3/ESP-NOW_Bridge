
#include <WiFi.h>
#include <esp_now.h>


esp_now_peer_info_t peerInfo;


// Callback when data is sent
void messageSent(const uint8_t *macAddr, esp_now_send_status_t status) {
    Serial.print("snd:");
    if(status == ESP_NOW_SEND_SUCCESS){
        Serial.println("1");
    }
    else{
        Serial.println("0");
    }
}


void messageReceived(const uint8_t* macAddr, const uint8_t* incomingData, int len){
  Serial.print("msg:");
  for(int i=0; i<6; i++){
    Serial.write(macAddr[i]);
  }
  for(int i=0; i<len; i++){
    Serial.print((char)incomingData[i]);
  }
  Serial.println();
}
 
void setup() {
  // Initialize Serial Monitor
  Serial.begin(230400);
  
  // Set device as a Wi-Fi Station
  WiFi.mode(WIFI_STA);

  // Init ESP-NOW
  if (esp_now_init() != 0) {
    Serial.println("Error initializing ESP-NOW");
  }

  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  
  esp_now_register_recv_cb(messageReceived);
  esp_now_register_send_cb(messageSent);

  Serial.println();
  Serial.print("mac:");
  Serial.println(WiFi.macAddress());
}

void loop() {
  if (!Serial.available()){
    return;
  }
  byte msg_len = 0;
  char msg_buffer[256];
  uint8_t address[6];

  for (int i=0; i<6; i++){
    byte num = Serial.read();
    address[i] = num;
  }
  
  msg_len = Serial.read();

  memcpy(peerInfo.peer_addr, address, 6);
  esp_now_add_peer(&peerInfo);
  
  for (int i=0; i<msg_len; i++){
    char c = Serial.read();
    msg_buffer[i] = c;
  }
  while (true){
    char c = Serial.read();
    if (c == '\n'){
      break;
    }
  }

  if(msg_len == 0){
    Serial.print("mac:");
    Serial.println(WiFi.macAddress());
  }else{
    esp_now_send(address, (uint8_t *) msg_buffer, msg_len);
  }
}
