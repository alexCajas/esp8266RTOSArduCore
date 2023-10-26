# Check ESP-IDF version and error out if it is not in the supported range.
#
# Note for arduino-esp32 developers: to bypass the version check locally,
# set ARDUINO_SKIP_IDF_VERSION_CHECK environment variable to 1. For example:
#   export ARDUINO_SKIP_IDF_VERSION_CHECK=1
#   idf.py build

# get path of core files and core libraries
get_filename_component(PARENT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)

set(CORE_DIR "${PARENT_DIR}/cores/esp8266")
set(LIBRARIES_DIR "${PARENT_DIR}/libraries")

set(CORE_SRCS
  ${CORE_DIR}/base64.cpp
  ${CORE_DIR}/cbuf.cpp
  #${CORE_DIR}/esp32-hal-adc.c
  #${CORE_DIR}/esp32-hal-i2c.c
  #${CORE_DIR}/esp32-hal-i2c-slave.c  
  #${CORE_DIR}/esp32-hal-psram.c
  #${CORE_DIR}/esp32-hal-sigmadelta.c
  #${CORE_DIR}/esp32-hal-spi.c
  ${CORE_DIR}/esp32-hal-time.c
  #${CORE_DIR}/esp32-hal-timer.c
  #${CORE_DIR}/Tone.cpp  
  #${CORE_DIR}/esp32-hal-tinyusb.c ?  
  ${CORE_DIR}/esp32-hal-cpu.c
  ${CORE_DIR}/esp32-hal-gpio.c
  ${CORE_DIR}/esp32-hal-misc.c
  ${CORE_DIR}/esp32-hal-uart.c
  ${CORE_DIR}/Esp.cpp
  ${CORE_DIR}/FunctionalInterrupt.cpp
  ${CORE_DIR}/HardwareSerial.cpp
  ${CORE_DIR}/IPAddress.cpp
  ${CORE_DIR}/IPv6Address.cpp
  ${CORE_DIR}/libb64/cdecode.c
  ${CORE_DIR}/libb64/cencode.c
  ${CORE_DIR}/main.cpp
  ${CORE_DIR}/MD5Builder.cpp
  ${CORE_DIR}/Print.cpp
  ${CORE_DIR}/stdlib_noniso.c
  ${CORE_DIR}/Stream.cpp
  ${CORE_DIR}/StreamString.cpp
  ${CORE_DIR}/wiring_pulse.cpp
  ${CORE_DIR}/wiring_shift.cpp
  ${CORE_DIR}/WMath.cpp
  ${CORE_DIR}/WString.cpp
  )

set(LIBRARY_SRCS
  #${LIBRARIES_DIR}/ArduinoOTA/src/ArduinoOTA.cpp
  #${LIBRARIES_DIR}/AsyncUDP/src/AsyncUDP.cpp
  #${LIBRARIES_DIR}/BluetoothSerial/src/BluetoothSerial.cpp
  #${LIBRARIES_DIR}/BluetoothSerial/src/BTAddress.cpp
  #${LIBRARIES_DIR}/BluetoothSerial/src/BTAdvertisedDeviceSet.cpp
  #${LIBRARIES_DIR}/BluetoothSerial/src/BTScanResultsSet.cpp
  #${LIBRARIES_DIR}/DNSServer/src/DNSServer.cpp
  #${LIBRARIES_DIR}/EEPROM/src/EEPROM.cpp
  #${LIBRARIES_DIR}/ESPmDNS/src/ESPmDNS.cpp
  #${LIBRARIES_DIR}/Ethernet/src/ETH.cpp
  #${LIBRARIES_DIR}/FFat/src/FFat.cpp
  ${LIBRARIES_DIR}/FS/src/FS.cpp
  ${LIBRARIES_DIR}/FS/src/vfs_api.cpp
  ${LIBRARIES_DIR}/HTTPClient/src/HTTPClient.cpp
  #${LIBRARIES_DIR}/HTTPUpdate/src/HTTPUpdate.cpp
  #${LIBRARIES_DIR}/LittleFS/src/LittleFS.cpp
  #${LIBRARIES_DIR}/Insights/src/Insights.cpp
  #${LIBRARIES_DIR}/I2S/src/I2S.cpp
  #${LIBRARIES_DIR}/NetBIOS/src/NetBIOS.cpp
  #${LIBRARIES_DIR}/Preferences/src/Preferences.cpp
  #${LIBRARIES_DIR}/RainMaker/src/RMaker.cpp
  #${LIBRARIES_DIR}/RainMaker/src/RMakerNode.cpp
  #${LIBRARIES_DIR}/RainMaker/src/RMakerParam.cpp
  #${LIBRARIES_DIR}/RainMaker/src/RMakerDevice.cpp
  #${LIBRARIES_DIR}/RainMaker/src/RMakerType.cpp
  #${LIBRARIES_DIR}/RainMaker/src/RMakerQR.cpp
  #${LIBRARIES_DIR}/RainMaker/src/RMakerUtils.cpp
  #${LIBRARIES_DIR}/SD_MMC/src/SD_MMC.cpp
  #${LIBRARIES_DIR}/SD/src/SD.cpp
  #${LIBRARIES_DIR}/SD/src/sd_diskio.cpp
  #${LIBRARIES_DIR}/SD/src/sd_diskio_crc.c
  #${LIBRARIES_DIR}/SimpleBLE/src/SimpleBLE.cpp
  #${LIBRARIES_DIR}/SPIFFS/src/SPIFFS.cpp
  #${LIBRARIES_DIR}/SPI/src/SPI.cpp
  #${LIBRARIES_DIR}/Ticker/src/Ticker.cpp
  #${LIBRARIES_DIR}/Update/src/Updater.cpp
  #${LIBRARIES_DIR}/Update/src/HttpsOTAUpdate.cpp
  #${LIBRARIES_DIR}/USB/src/USBHID.cpp
  #${LIBRARIES_DIR}/USB/src/USBHIDMouse.cpp
  #${LIBRARIES_DIR}/USB/src/USBHIDKeyboard.cpp
  #${LIBRARIES_DIR}/USB/src/USBHIDGamepad.cpp
  #${LIBRARIES_DIR}/USB/src/USBHIDConsumerControl.cpp
  #${LIBRARIES_DIR}/USB/src/USBHIDSystemControl.cpp
  #${LIBRARIES_DIR}/USB/src/USBHIDVendor.cpp
  #${LIBRARIES_DIR}/USB/src/USBVendor.cpp
  ${LIBRARIES_DIR}/WebServer/src/WebServer.cpp
  ${LIBRARIES_DIR}/WebServer/src/Parsing.cpp
  ${LIBRARIES_DIR}/WebServer/src/detail/mimetable.cpp
  ${LIBRARIES_DIR}/WiFiClientSecure/src/ssl_client.cpp
  #${LIBRARIES_DIR}/WiFiClientSecure/src/esp_crt_bundle.c
  ${LIBRARIES_DIR}/WiFiClientSecure/src/WiFiClientSecure.cpp
  ${LIBRARIES_DIR}/WiFi/src/WiFiAP.cpp
  ${LIBRARIES_DIR}/WiFi/src/WiFiClient.cpp
  ${LIBRARIES_DIR}/WiFi/src/WiFi.cpp
  ${LIBRARIES_DIR}/WiFi/src/WiFiGeneric.cpp
  ${LIBRARIES_DIR}/WiFi/src/WiFiMulti.cpp
  ${LIBRARIES_DIR}/WiFi/src/WiFiScan.cpp
  ${LIBRARIES_DIR}/WiFi/src/WiFiServer.cpp
  ${LIBRARIES_DIR}/WiFi/src/WiFiSTA.cpp
  ${LIBRARIES_DIR}/WiFi/src/WiFiUdp.cpp
  #${LIBRARIES_DIR}/WiFiProv/src/WiFiProv.cpp
  #${LIBRARIES_DIR}/Wire/src/Wire.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/MqttBroker/MqttBroker.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/MqttClient/MqttClient.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/MqttMessages/SubscribeMqttMessage.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/MqttMessages/AckConnectMqttMessage.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/MqttMessages/MqttMessage.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/MqttMessages/PublishMqttMessage.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/MqttMessages/ReaderMqttPacket.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/MqttMessages/ConnectMqttMessage.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/MqttMessages/UnsubscribeMqttMessage.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/MqttMessages/FactoryMqttMessage.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/TopicTree/NodeTrie.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/TopicTree/Trie.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/ConcurrentTasks/FreeMqttClientTask.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/ConcurrentTasks/NewClientListenerTask.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/ConcurrentTasks/TCPListenerTask.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/Actions/PublishAction.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/Actions/ActionFactory.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/Actions/DisconnectAction.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/Actions/NoAction.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/Actions/UnSubscribeAction.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/Actions/PingResAction.cpp
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src/Actions/SubscribeAction.cpp
  ${LIBRARIES_DIR}/WrapperFreeRTOS/src/Task.cpp
  )


set(includedirs
  #variants/${CONFIG_ARDUINO_VARIANT}/
  ${CORE_DIR}/
  #${LIBRARIES_DIR}/ArduinoOTA/src
  #${LIBRARIES_DIR}/AsyncUDP/src
  #${LIBRARIES_DIR}/BLE/src
  #${LIBRARIES_DIR}/BluetoothSerial/src
  #${LIBRARIES_DIR}/DNSServer/src
  #${LIBRARIES_DIR}/EEPROM/src
  #${LIBRARIES_DIR}/ESP32/src
  #${LIBRARIES_DIR}/ESPmDNS/src
  #${LIBRARIES_DIR}/Ethernet/src
  #${LIBRARIES_DIR}/FFat/src
  ${LIBRARIES_DIR}/FS/src
  ${LIBRARIES_DIR}/HTTPClient/src
  #${LIBRARIES_DIR}/HTTPUpdate/src
  #${LIBRARIES_DIR}/LittleFS/src
  #${LIBRARIES_DIR}/Insights/src
  #${LIBRARIES_DIR}/I2S/src
  #${LIBRARIES_DIR}/NetBIOS/src
  #${LIBRARIES_DIR}/Preferences/src
  #${LIBRARIES_DIR}/RainMaker/src
  #${LIBRARIES_DIR}/SD_MMC/src
  #${LIBRARIES_DIR}/SD/src
  #${LIBRARIES_DIR}/SimpleBLE/src
  #${LIBRARIES_DIR}/SPIFFS/src
  #${LIBRARIES_DIR}/SPI/src
  #${LIBRARIES_DIR}/Ticker/src
  #${LIBRARIES_DIR}/Update/src
  #${LIBRARIES_DIR}/USB/src
  ${LIBRARIES_DIR}/WebServer/src
  ${LIBRARIES_DIR}/WiFiClientSecure/src
  ${LIBRARIES_DIR}/WiFi/src
  #${LIBRARIES_DIR}/WiFiProv/src
  #${LIBRARIES_DIR}/Wire/src
  ${LIBRARIES_DIR}/EmbeddedMqttBroker/src
  ${LIBRARIES_DIR}/WrapperFreeRTOS/src
  )

set(srcs ${CORE_SRCS} ${LIBRARY_SRCS})
set(priv_includes ${CORE_DIR}/libb64)
set(requires spi_flash mbedtls mdns wifi_provisioning wpa_supplicant http_parser)
set(priv_requires fatfs nvs_flash app_update spiffs bootloader_support openssl)

idf_component_register(INCLUDE_DIRS ${includedirs} PRIV_INCLUDE_DIRS ${priv_includes} SRCS ${srcs} REQUIRES ${requires} PRIV_REQUIRES ${priv_requires})