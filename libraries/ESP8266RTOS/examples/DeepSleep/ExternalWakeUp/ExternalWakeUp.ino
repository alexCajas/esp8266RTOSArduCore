/*
Deep Sleep with External Wake Up for esp8266 based on 
Deep Sleep with External Wake Up esp32 arduino core by Pranav Cherukupalli <cherukupallip@gmail.com> 
=====================================
This code displays how to use deep sleep with
an external trigger as a wake up source and how
to store data in RTC memory to use it over reboots

This code is under Public Domain License.

Hardware Connections
======================
Push Button to rst pin pulled down with a 10K Ohm
resistor

Author:
Pranav Cherukupalli <cherukupallip@gmail.com>
2023 - Modify for esp8266 rtos arduino core by Alex Cajas <alexcajas505@gmail.com>
*/



RTC_DATA_ATTR int bootCount = 0;


void setup(){
  Serial.begin(115200);
  delay(1000); //Take some time to open up the Serial Monitor

  //Increment boot number and print it every reboot
  ++bootCount;
  Serial.println("Boot number: " + String(bootCount));


  //Go to sleep now
  Serial.println("Going to sleep now");
  ESP.deepSleep(0);

}

void loop(){

  Serial.println("This will never be printed");
}
