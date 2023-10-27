/*
Simple Deep Sleep with Timer Wake Up for esp8266 based on 
Simple Deep Sleep with Timer Wake up esp32 arduino core by Pranav Cherukupalli <cherukupallip@gmail.com> 
=====================================
ESP32 offers a deep sleep mode for effective power
saving as power is an important factor for IoT
applications. In this mode CPUs, most of the RAM,
and all the digital peripherals which are clocked
from APB_CLK are powered off. The only parts of
the chip which can still be powered on are:
RTC controller, RTC peripherals ,and RTC memories

This code displays the most basic deep sleep with
a timer to wake it up and how to store data in
RTC memory to use it over reboots

This code is under Public Domain License.

Important: When timer is fired hardware send a signal throught D0 pin. 
You need connect D0 pin to rst pin to wake up from deep sleep.

Author:
Pranav Cherukupalli <cherukupallip@gmail.com>
2023 - Modify for esp8266 rtos arduino core by Alex Cajas <alexcajas505@gmail.com>
*/

#define uS_TO_S_FACTOR 1000000ULL  /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP  5        /* Time ESP32 will go to sleep (in seconds) */

RTC_DATA_ATTR int bootCount = 0;

void setup(){
  Serial.begin(115200);
  delay(1000); //Take some time to open up the Serial Monitor

  //Increment boot number and print it every reboot
  ++bootCount;

  Serial.println("Boot number: " + String(bootCount));
  Serial.println("Setup ESP32 to sleep for every " + String(TIME_TO_SLEEP) +
  " Seconds");
  Serial.println("don't forget connect D0 pin to rst pin, to wakeup from deep sleep!");

  Serial.println("Going to sleep now");
  Serial.flush(); 
  ESP.deepSleep(TIME_TO_SLEEP * uS_TO_S_FACTOR);
  Serial.println("This will never be printed");
}

void loop(){
  //This is not going to be called
}
