#include <WiFiClientSecure.h>

const char* ssid     = "your-ssid";     // your network SSID (name of wifi network)
const char* password = "your-password"; // your network password

const char*  server = "www.howsmyssl.com";  // Server URL

WiFiClientSecure client;

void sslInsecureExample(void *args);
void setup() {
  //Initialize serial and wait for port to open:
  Serial.begin(115200);
  delay(100);

  Serial.print("Attempting to connect to SSID: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  // attempt to connect to Wifi network:
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    // wait 1 second for re-trying
    delay(1000);
  }

  Serial.print("Connected to ");
  Serial.println(ssid);

  xTaskCreate(&sslInsecureExample, "ssl insecure example task", 8192, NULL, 5, NULL);

}

void loop() {
  // do nothing
  vTaskDelay(1);
}

void sslInsecureExample(void *args){

  Serial.println("\nStarting connection to server...");
  client.setInsecure();//skip verification

  while(true){

    if (!client.connect(server, 443)){
      Serial.println("Connection failed!, waiting 500mlsec until retry connection again");
      vTaskDelay(500);
    }
      
    else {
      Serial.println("Connected to server!");
      // Make a HTTP request:
      client.println("GET https://www.howsmyssl.com/a/check HTTP/1.0");
      client.println("Host: www.howsmyssl.com");
      client.println("Connection: close");
      client.println();

      while (client.connected()) {
        String line = client.readStringUntil('\n');
        if (line == "\r") {
          Serial.println("headers received");
          break;
        }
      }
      // if there are incoming bytes available
      // from the server, read them and print them:
      while (client.available()) {
        char c = client.read();
        Serial.write(c);
      }

      client.stop();
      Serial.println();
      Serial.println("connection closed");
      vTaskDelete(NULL);
    }
  }
}
