/*
*  Print last reset reason of ESP8266
*  =================================
*
*  Use either of the methods print_reset_reason
*  or verbose_print_reset_reason to display the
*  cause for the last reset of this device.
*
*  Public Domain License.
*
*  Author:
*  Evandro Luis Copercini - 2017
*  2023 - adapt for esp8266 rtos ardu core by Alex Cajas <alexcajas505@gmail.com>
*/

#include <esp_system.h>

#define uS_TO_S_FACTOR 1000000  /* Conversion factor for micro seconds to seconds */

void print_reset_reason(esp_reset_reason_t reason)
{
  switch ( reason)
  {
  case 1:
    Serial.println("ESP_RST_POWERON");
    break; /**<1,  Vbat power on reset*/
  case 3:
    Serial.println("ESP_RST_SW");
    break; /**<3,  Software reset digital core*/
  case 4:
    Serial.println("ESP_RST_PANIC");
    break; /**<4,  Software reset due to exception/panic*/
  case 5:
    Serial.println("ESP_RST_INT_WDT");
    break; /**<5,  Reset (software or hardware) due to interrupt watchdog*/
  case 6:
    Serial.println("ESP_RST_TASK_WDT");
    break; /**<6,  Reset due to task watchdog*/
  case 7:
    Serial.println("ESP_RST_WDT");
    break; /**<7,  Reset due to other watchdogs*/
  case 8:
    Serial.println("ESP_RST_DEEPSLEEP");
    break; /**<8,  Reset after exiting deep sleep mode*/
  case 9:
    Serial.println("ESP_RST_BROWNOUT");
    break; /**<9,  Brownout reset (software or hardware)*/
  case 10:
    Serial.println("ESP_RST_SDIO");
    break; /**<10, Reset over SDIO*/
  case 11:
    Serial.println("ESP_RST_FAST_SW");
    break; /**<11, Fast reboot*/
  default:
    Serial.println("NO_MEAN");
  }
}

void verbose_print_reset_reason(esp_reset_reason_t reason)
{
  switch ( reason)
  {
  case 1:
    Serial.println("Vbat power on reset");
    break; /**<1,  Vbat power on reset*/
  case 3:
    Serial.println("Software reset digital core");
    break; /**<3,  Software reset digital core*/
  case 4:
    Serial.println("Software reset due to exception/panic");
    break; /**<4,  Software reset due to exception/panic*/
  case 5:
    Serial.println("Reset (software or hardware) due to interrupt watchdog");
    break; /**<5,  Reset (software or hardware) due to interrupt watchdog*/
  case 6:
    Serial.println("Reset due to task watchdog");
    break; /**<6,  Reset due to task watchdog*/
  case 7:
    Serial.println("Reset due to other watchdogs");
    break; /**<7,  Reset due to other watchdogs*/
  case 8:
    Serial.println("Reset after exiting deep sleep mode");
    break; /**<8,  Reset after exiting deep sleep mode*/
  case 9:
    Serial.println("Brownout reset (software or hardware)");
    break; /**<9,  Brownout reset (software or hardware)*/
  case 10:
    Serial.println("Reset over SDIO");
    break; /**<10, Reset over SDIO*/
  case 11:
    Serial.println("Fast reboot");
    break; /**<11, Fast reboot*/
  default:
    Serial.println("NO_MEAN");
  }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  delay(2000);

  Serial.println("CPU0 reset reason:");
  print_reset_reason(esp_reset_reason());
  verbose_print_reset_reason(esp_reset_reason());



  // Set ESP32 to go to deep sleep to see a variation
  // in the reset reason. Device will sleep for 5 seconds.
  Serial.println("Going to sleep");
  ESP.deepSleep(5 * uS_TO_S_FACTOR);
}

void loop() {
  // put your main code here, to run repeatedly:

}

/*
  Example Serial Log:
  ====================

rst:0x5 (DEEPSLEEP_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
configsip: 0, SPIWP:0x00
clk_drv:0x00,q_drv:0x00,d_drv:0x00,cs0_drv:0x00,hd_drv:0x00,wp_drv:0x00
mode:DIO, clock div:1
load:0x3fff0008,len:8
load:0x3fff0010,len:160
load:0x40078000,len:10632
load:0x40080000,len:252
entry 0x40080034
CPU0 reset reason:
ESP_RST_DEEPSLEEP
Reset after exiting deep sleep mode
Going to sleep

*/
