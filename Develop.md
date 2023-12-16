# Develop

esp8266RTOS sdk for arduino.


# Notes

* SDK: master commit 35375c17

* in board.txt it is defined de path of core, so if you delete cores direcotory from the sdk, arduino ide will show error message saying, "it can't open path/cores/esp8266"


* sdkconfig.h se puede resolver en tiempo de compilacion cuando idf lo genere en {build.path}/config


* opciones de compilado: las opciones de compilado de tools/build.cmake se escriben justo despues de las añadidas en project/CMakeList.txt, el compilador, por ejemplo, añado en project/cmake  -std=gnu++17, pero en tools/build.cmake está definido -std=gnu++11, al compilador le llega -c -.... -std=gnu++17 -.... -std=gnu++11, tomando esta última como standar a añadir.

* Desde components/arduino/Cmake si se prioriza el estandar definido ahí a la hora de compilar, no obstante no sale del ámbito del componente. 

* Opto por quitar las opciones de compilacion de tools/ y de sdk/ para que se usen las de project/cmake

## Windows:

* Msys2 from spressif hasn't cmake and it can install new software, soluction, download oficial msys2, install cmake and copy cmake files to msys-spressif, the files are in mingw64 (see offical cmake package for msys2)

* in msys32/etc/profile add at the end the folowing lines: export PATH=$PATH:/mingw64/bin
export PATH=$PATH:/mingw32/bin to add python and cmake to path.

* then you are available to install requeriments.txt 

# V1.0.1

### To do

* Adding windows OS compatibility.
* Idea, write python script to prepare all directories and files to compile the idf project.
* Use .sh and .bat only to call idf tools (build and flash) 

* Severals isues in windows:
  * if you write and sketch.ino and .cpp file in the same directory, arduino cli doesn't create sketch.ino.cpp in build/skecth, it create .cpp.cpp, this issue is not in linux.
  * continues verify call  creates build directorys in build/sketch, I don't test the new script in linux, but porbably this issue is not present in linux --> tested in linux all is ok, the issue is from arduino cli in windows.

* In linux the .cpp file added next to sketch.ino is not included well in cmakelist.txt, the system looking for the file in Arduino/libraries but it is in idfTemplate/main together to sketch.ino.cpp

* Scripts.py tested in linux all is ok! it works!
* remain compile.bat and flash.bat to use msys2 to build and flash idf project.

## done

* createPreproc.py, it replace preCompile.sh
* createTemplate.py, it repalce idfTemplate configuration in compile.sh
* createCmake.py, it replace createProject.py
* dummy.py, it replace dummy.sh
* modified get_include_files.py now receive the path of arduino/libraries like argument
* windowsPathToUnixPath.bat
* severals .bat to test, this .bat can be removed

---

# V1.0.0

## current status:

* compiling wiht gnu99 and gnu++11, try to change to gnu17 and gnu++17

* There are an python enviorement where are requeriments.txt rtosSDK installed. It is needed to activate before to use idf

* It is possible to compile and upload an sketch.ino from aruino ID:
  * It is needed add app_main() function manualy.

* There is an basic arduino wrapper functions.

## Core implementation:

* I will use esp32 core like comoponent, to implement my own esp8266 core like component, the key is that, esp32 core like component is also esp32 core arduino.

* Using that together platform.txt and board txt I can get arduino ide build and flash idfprojects!. 

## To Do

* Esp.h: some functios availables on esp32, are not adapted to esp8266, think if is posible.
* Think in add #if TARGET_CONF_esp32 to more compatibility. --> I think that is a good idea because RTOS is more ligth than FreeRtos used in esp32.




* WiFiServer: allways return a wifiClient, but in the original implementation return NULL, looking for the way to return NULL and no t empty WiFiClient for compatibilitie: for example check if(!client) return always false, becaude always it is returned a WiFiClient object

* rewrite paltafrom.txt to give support to compile options, now it is not implement.

* Add pins support for more models of esp8266.

* think in to use of export.sh instead of export idf and xtensa manually in the scritps.

* changes my scritps.sh to .py (compilar.sh, flash.sh preCompile.sh, and dummy.sh) to be more compatible between OS.

## Doing

* It can't compile externa libraries!!:
  * Version of cmake that include all cpp and get .h directory like src!--> done
  * Version that looking for #include librarie doing, see Escritorio/cmakeTest: Idea, find "file.h" get his direcory, find all .c .cpp in this directory, add to dependencies directory and files in idfTemplate cmake:
    * doing in include_files.py: now create a json with .c and .cpp files and .h directoris of all #includes headers. looking for in Arduino/libraries:
      * now filter only in root directory of file.h and src/ to include .c or .cpp files.
      * Create includes.json in idfTemplate/main
      * Now createProject.py can read includes.json and add srcs and includedirst to cmakeList.txt.
      * Finish functional version, now script is get_include_files.py:
        * it is not recursive, only resolve dependencies in sckets.ino headers includes, if some of this headers have dependencies with other header of other librarie not includen in sckets.in it can't resolve this recursive dependencie, you need to include all depedencies in stacketch.ino
   

* Make a list with esp32 core libraries to test and fix!:

- [x] WiFi
- [x] EmbeddedMqttBroker
- [x] WrapperFreeRTOS
- [x] WebServer
- [x] WiFiClientSecure
- [x] WiFiProv
- [x] HTTPClient
- [ ] HttpUpdate
- [ ] HttpUPdateServer
- [x] DNSServer
- [x] ESPmDNS
- [ ] AyncUDP?
- [ ] Update
- [ ] ArduinoOta
- [ ] EEPROM
- [ ] ESP[32|8266] examples
- [ ] FFat
- [ ] FS
- [ ] NetBios
- [ ] Preferences?
- [ ] SD
- [ ] SDMMC?
- [ ] SPI
- [ ] SPIFFS
- [ ] Ticker
- [ ] Wire



* hardware dependecies files to do: 

- [ ]  #${CORE_DIR}/esp32-hal-adc.c
- [ ]  #${CORE_DIR}/esp32-hal-i2c.c
- [ ]  #${CORE_DIR}/esp32-hal-i2c-slave.c
- [ ]  #${CORE_DIR}/esp32-hal-psram.c
- [ ]  #${CORE_DIR}/esp32-hal-sigmadelta.c
- [ ]  #${CORE_DIR}/esp32-hal-spi.c
- [x]  #${CORE_DIR}/esp32-hal-time.c
- [ ]  #${CORE_DIR}/esp32-hal-timer.c
- [ ]  #${CORE_DIR}/Tone.cpp
- [ ]  #${CORE_DIR}/esp32-hal-tinyusb.c ?
    

* hardware dependencies files not used in this sdk:

  * esp32-hal-dac.c
  * esp32-hal-bt.c
  * #${CORE_DIR}/esp32-hal-ledc.c
  * #${CORE_DIR}/esp32-hal-matrix.c
  * #${CORE_DIR}/esp32-hal-rgb-led.c
  * #${CORE_DIR}/esp32-hal-touch.c
  * #${CORE_DIR}/esp32-hal-rmt.c
  * #${CORE_DIR}/USB.cpp
  * #${CORE_DIR}/USBCDC.cpp
  * #${CORE_DIR}/USBMSC.cpp
  * esp32-hal-touch.c
  * #${CORE_DIR}/HWCDC.cpp
  * #${CORE_DIR}/FirmwareMSC.cpp
  * #${CORE_DIR}/firmware_msc_fat.c


* test and fix libraries of core of esp32 in this core (WiFi, WebServer, ArduinoOta etc...):
  * WiFiClientSecure v1.0.6: --> done
    * need active CONFIG_ESP_TLS_PSK_VERIFICATION in sdkconfig
    * Bug Stack canary watchpoint triggered (uiT) bad storeLoad, difference between WiFiClient.hpp
    * and ssl_client.cpp is use lwip_socket(), WiFiClient use:
    ~~~
    socket(AF_INET, SOCK_STREAM, 0){} that call to lwip_socket(AF_INET, SOCK_STREAM, 0).
   ~~~
   * And ssl_client.cpp call directly to lwip_socket() with (AF_INET, SOCK_STREAM, IPPROTO_TCP)
      * Code works well until call to   
        ~~~
        err_t // this function is in sys_arch.c freertos version!.
        sys_mbox_new(sys_mbox_t *mbox, int size){
              .
              .
              .
          LWIP_DEBUGF(ESP_THREAD_SAFE_DEBUG, ("new *mbox ok mbox=%p os_mbox=%p\n", *mbox, (*mbox)->os_mbox));
        }
        
        ~~~
  * more info: client insecure works find!!.
  * I try to comment client.setCACert(test_root_ca);, and now stack canary watchdog is no fired, so problem is in this way!!:
    * When I change  test_root_ca to a short mesagge "hello\n", the code works well, lwip_socket connect the socket well, and sll protocol don't run because test_root_ca don't have ca format. ¿Maybe ca is too long for esp8266 memory?:
      * The problem is when try to get handshake in ssl_tls.c:
      ~~~
  int mbedtls_ssl_handshake( mbedtls_ssl_context *ssl )
  {   printf("entry in mbdtls_ssl_handshake\n");
      int ret = 0;

      if( ssl == NULL || ssl->conf == NULL )
          return( MBEDTLS_ERR_SSL_BAD_INPUT_DATA );

      MBEDTLS_SSL_DEBUG_MSG( 2, ( "=> handshake" ) );

      while( ssl->state != MBEDTLS_SSL_HANDSHAKE_OVER )
      {   
          printf("affer this is fired stackcanary\n");
          ret = mbedtls_ssl_handshake_step( ssl );
          printf("ret getted\n");
          if( ret != 0 )
              break;
      }

      MBEDTLS_SSL_DEBUG_MSG( 2, ( "<= handshake" ) );
      printf("mbdtls_ssl_ret %d\n",ret);
      return( ret );
  }      
      ~~~
  * ssl_client call to this function in while function, eventualy in one iteration, the stack canary watchdog storeLoad is fired!:
  
  * I tested https_medtls example of rtos, and it work well, I use this example to create a test in arduino core and it work well even using example CA of esp32 --> Idea, changes ssl_client.cpp acording to rtos example:
    * Fixed!, the issue comes from setup() and loop(), for some reason mbedtls loops fire stack canary watchdog affter few iterations,  but in another task it run well!
    * The problem was that loop and setup was no running in his own task. Solved. The original examples of this libraries works well!.
  
  * HttpClient v1.0.6: --> done
  
  * FS --> test with WebServer: Validated

  * WebServer: --> validated
    * Added http_parser dependency in arduino/CMakeLists.txt
  
  * ESPmDNS --> validated 

  * WiFiProvi:  --> validated
    * Removed all lines refenced to BLE provisioning

  * AsyncUDP:
    * testar luego NetBios.

  * Update --> httpUpdate --> ArduinoOta

## Done

### 22/10/2023

* Hardware dependencies: A lot circular dependencies in hal.h, I decided quit includes in hal.h and add the necesary include in the particulars files that need it.  --> That was not the problem, was a lost referency to base_t because I don't include freertos in hal.h, probabli in next iterations I will leave the includes in hal.h and other like esp32 core--> done

### --/--/--

* cores/esp8266 is needed to arduino cli can run, so I prefer move arduino component to this directory in the future.

* refactor folding proyect to delete all reference to nonosSDK arduino core

* CoreNotes:
	* write Arduino.h wrapper for all utilites of esp8266 for RTOS sdk:
    	* I think that the best way to do that, is implementing each function of esp32/Arduino.h, to get the same interfaz likes esp32-Arduino core, this idea limit the options of configure that nonosSDK give us. 	
	* implement that like a idf component --> done
  
	* researh how to use external libraries with idf, the idea is implement arduino core in ./cores/esp8266 and link that with components or in CMaskeLists.txt or some similar. --> using cmake like esp32 core (idf component) --> done
	* Write arduino/cmake using esp32 core (idf component) like referene --> done

* delete comments in platform and scritps before publish

* rewrtie package.json and board.txt to be installed by Arduino platform: see notesForPublisCore.md --> done.

* Issue3: Problems with wifiClient, try to use EmbeddedMqttBroker, when new mqtt client is connect, some troubles with fd appears --> The problem is that, when WiFiClient return a new client it is called to ~WiFiClient() and this method close fd:
  * after this line:remainingLengt = readRemainLengtSize(client); client socket is closed just after return value of readRemainLengtSize() function.
  * When you give a class like value in the argument of a function, c++ call a copy function to use it in the scop of the function called, and when the function is finished, destructor of copied object is called to. Here is the problem!:
    * The solution is create my own copy constructor method.  

## Core Files
  
### not hardware dependencies

    * binary.h --> done tested ok
    * stdlib_noniso.c --> done tested ok
    * stdlib_noniso.c --> done tested ok
    * WCharacter.h --> done tested ok
    * pgmspace.h --> done Used in Wstring.h tested ok
    * Wstring.h --> done (fixed components/aruduino/cmake), tested ok
    * base64 --> done, tested ok
    * libb64/ --> done, tested ok
    * Print.h --> done,tested ok
    * Printable.h --> done,tested ok
    * IPAAddres.h --> done, tested ok
    * IPv6Addres.h --> done, tested ok
    * Printable.h --> done, tested ok since HardwareSerial.h was tested.
    * Server.h --> done tested, ok
    * Udp.h --> done, tested ok
    * cbuf.h --> done, tested ok
    * FunctionalInterrupt.h --> done, tested ok since HardwareSerial.h

### with hardware dependencies
  
    * esp32-hal.h: In RTOS is not implement watch dog disable --> changes some funtions to be adapted to RTOS core
    
    * esp32-misc.c: ---> validated, done
      * use esp32-hal-log --> done 
      * esp32-hal-cpu.c(setCpuFrequencyMhz) --> done
      
    * esp-hal-log.h: --> done and tested
      * esp32-hal-uart (log_printf) --> done
      * hal-misc.c (path_tofilename) --> done

    * Stream.h: --> compile, done tested ok
      * esp32-hal-misc.h --> done

    * HardwareSerial: --> no compile fail hal.h, --> done and tested!
      * esp32-hal-uart --> done, and tested!
      * Stream.h --> like interfaz, done and tested!
      * esp32-hal-log.h --> done!
      * pins_arduino.h --> for now its only one variant support 
      * commons.h -> used for pins_arduino.h

  
    * esp32-hal-uart:  --> compile ok, but need test with Serial.begin etc --> tested! ok!
      * espre-hal-matrix -->(control of led matrix) no supperted by esp8266
      * esp32-hal-gpio.h  --> done
      * esp32-hal-cpu --> done
      
    * esp32-hal-cpu: --> done 
      * esp32-hal-log --> done
    
    * esp32-hal-gpio.h --> done and tested, but I had problems in compiling time when include this library to hal.h, so I remove hal.h include from gpio.h, and add gio.h include in hal.h. 

    * MD5Builder.h --> tested Ok
      * Stream.h --> done

    * ESP.h: --> done
      * MD5Builder.h --> done
      * WString  --> done
    
    * StreamString.h --> done and tested ok

    * WMath.cpp: done, tested ok
      * hal-log.h --> done

    * wiring_pulse.c: --> tested ok
      * changes: wiring_pulse.c to wiring_pulse.cpp
      * added include #<limits.h> library
      * hal-gpio.h --> done
      * wiring_private.h --> done
      * hal-cpu.h --> done
    * wiring_shift.c: --> tested ok
      * changes wiring_shift.c to wiring_shift.cpp
      * hal-gpio.h --> done
      * wiring_private.h --> done


### libries:
  * WiFi: since LWIPSafeThread 45abc586, I decided to rewrite all this library, trying to get the same API offered by esp32ArduinoCore: --> done!
    * To implement the library, I will use WiFiLibrary branch, this branch has an adaptaption of this library to use unsafe lwip version, but it has issues to process the sockets y an server and in an client, but connect WiFiSta problably WiFiAp, work find. So I will changes client and server class

    * It is necesary to enable CONFIG_ENABLE_UNIFIED_PROVISIONING, it can be set in sdkconfig, I add this in sdconfig of idfTemlate 
      * adataptions esp32 -> esp8266:
        * lwip/socket de lwip_ioctl_r --> lwip_ioctl, lwip_ioctl_r is an reentrant version, used for safe-trhead. 


      * Remove esp_ipc.h --> api to talk between cores.

      * WiFiGeneric.h: --> compile
        * Added #define CONFIG_ARDUINO_EVENT_RUNNING_CORE 0, In the future, add this flag in sdkconfig, and remove of generic.h 
        * It is the base to WiFiSTA AP and scan
        * how this classes are validate, this library to.
        
      
      * WiFi.h --> compile and upload, tested ok, it can connect correctly to the wifi. Validate ok!
        * WiFi.h it is a class to wrapp: 
          *  public WiFiSTAClass  --> ok
          *  public WiFiScanClass  --> ok 
          *  public WiFiAPClass --> ok
       *  this class use WiFiGeneric like father.
  
      * WiFiSTAClass: --> compile and tested! ok, tested with esp client not WiFiClient
        * Added freertos to eventgroups
        
        * WiFiSTA 
        * .h:
          * changed signature of callback to static void _smartConfigCallback(void* arg, esp_event_base_t base, int32_t event_id, void* data);
        * .c:
          *  modify beginSmartConfig, esp_smartconfig_start has a new signature:
            ´´´
              esp_wifi_disconnect();
              smartconfig_start_config_t config;
              esp_err_t err;
              err = esp_smartconfig_start( &config, reinterpret_cast<sc_callback_t>(&WiFiSTAClass::_smartConfigCallback));

            ´´´
          * changed _smartconfigcallback:

              ´´´
              void WiFiSTAClass::_smartConfigCallback(void* arg, esp_event_base_t base, int32_t event_id, void* data) {

                  #if ARDUHAL_LOG_LEVEL >= ARDUHAL_LOG_LEVEL_DEBUG
                      log_d("sended ack");
                  #endif

                  WiFi.stopSmartConfig();
                  
              }
              ´´´
        * smartconfig.h:
        
          *  added callback when smartconfig send ack to finish smartconfig:
            
             *  typedef void (*sc_callback_t)(void* arg, esp_event_base_t base, int32_t event_id, void* data);
          
          *  Changed signature of esp_smartconfig_start to recive callback: 
             
             *   esp_smartconfig_start(const smartconfig_start_config_t* config,sc_callback_t cb);
         
         *   smartconfig.c:
             
             * Changed signature of esp_smartconfig_start to receive callback:
               
               * esp_smartconfig_start(const smartconfig_start_config_t* config,sc_callback_t cb);  :
                
                 * register callback in esp_smartconfig:
                  
                   * esp_event_handler_register(SC_EVENT, SC_EVENT_SEND_ACK_DONE, cb, NULL);
                 
                 * unregister callback in case of error:
                  
                   * esp_event_handler_unregister(SC_EVENT, SC_EVENT_SEND_ACK_DONE, cb);
        
        * Added that, I get compatibilite with esp32::WiFiSTA.cpp  

      * WiFiAPClass: --> tested, all ok
          * compile ok 
          * deploy de network ok, 
          * handle a client of network ok

        * Basically use WiFiGeneric, and is an light wrapper of esp_wifi
        * Problems with watchdog, triggered time fired allways in this mode.

      * Wifi AP+STA mode:
        * all ok!
      
      * WiFiSan: it is an light wrapper to,
        * Tested all ok!

      * WiFiMulti.h: --> tested all ok
        * need WiFi.h --> done

      * WiFiServer: --> validate ok!
        * Change LWIP reentrant methods to normal methods (LWIP used in RTOS doesn't has reentrant methods.)
        
        * Can't handle a get/post request!:
          
          * The problem is the WiFiClient class: 
            * to figure that, I changed WiFiServer::WiFiClient available to WiFiServer::int available, returning the client_fd_socket, then I use this fd to talk with tcp client and all was good!
      
      * WiFiClient:
        * request ok, but can't get response.
         
        * Need LWIP_SO_RCVBUF to be available to read of socket.
        
        * There still firing Store load core dump:
          
          *  The store load is fired by std::shared_ptr! this library is introduced in c++11, I tried to compile with that, but it dind't work, so I compiled with c++20 and the issue still there:
             *  I test shared_ptr with nonos sdk and it work find, I checked the c++ compiler, it use c++17, I will try to use that:
                *  I  having problems to set c++ standar in idf, I changes in projec/cmake but I can't get any change, it is because tools/cmake/cmake.build is include at the end of the compiple option, overriding the options setted in project/CMakeLists.txt. more in Notes section in this readme.
                   *  Solution comment options in cmake.build and idf/CMake to use only options in project/Cmake:
                      *  fail, trubbles in compiling time, bootloader can't link well with severals libaries. So I will enable one by one the options untill I get a well link:
                         *  Don't work, I readed that the problem is the verion of compiler [https://github.com/espressif/ESP8266_RTOS_SDK/issues/991], so I triying to use older version of this:
                            *  don't work, severals issues when link code between libraries. I will try to use older version of sdk+older versions of compiler:
                               *  I get to use std::shared, using sdk release3.2 and xtensa-lx106-elf-linux64-1.22.0-92-g8facf4c-5.2.0, 
                               *  using sd release 3.3 and the same version of toolchain ok!
                               *  Using sdk 3.4 it can't compile with 5.2.0, but yes with 8.4.0, and fail sdt::shared_ptr:
                                  *  I got to compile using sdk 3.4 (master commit) with toolchain 5.2.0, the issue was a lib included in toochaing v8.4.0 but not in v5.2.0, I only added this lib from v8.0.4 to v5.2.0 and all was good!, compile well and std::shared_ptr din't crash!. The lib is nano:
                                     *  Triying to use 3.4 sdk and 5.2.0 toolchain, others problems in compile time are fired, so I will try to move arduino component to 3.3:
                                        *  fail, 3.4 has diferents functionalities used by this project, and the compile of project is not easy, I couldn't compile adding WiFi.h. Final desicion, change std::shared_ptr fo std::unique_ptr:
                                           *  this makes not sense, because std::shared_ptr is used for share referencies, and unique is the opposite, so to get this sentence ok
                                           ´´´
                                            WiFiClient c = server.available();
                                           ´´´
                                           It is needed to share this ptr. So I implement this library using a int countRef, to manages the memory.
                                

      * WiFiUdp: tested, ok, not changes to adapt to esp8266RTOS
    * LWIP Issue: the version of lwip in esp8266RTOS is an version unsafe-thread, so I need to rewrite WiFi library with functions no reentrants. Other options y changes the version of LWIP used for the version used in Esp32 idf.
      * I will test the last option --> If I use lwip of idf, it will be a lo dependencies with esp32. The official version is unsafe-thread.
      * Solution: change to unsafe version of WiFi, and use mutex in high level threads, it is not efficient in time but in futures version of esp8266RTOS sdk will be availabe an safe thread version.


---

* ESP.h, implemented, tested ok

* hal-log.h --> done

* Think how to link Arduino/main.cpp in the .ino.cpp file, because idf search this function to start. -- > I add manually this code in .ino:
  * For now I copy main.cpp in sktech/main/ and add in cmake the file
  * Probably it can be do better using cmake to link main.cpp of componentes/Arduino/include, to the project.:
    * I am using esp32 core like idf component, to implement esp8266 core like idf component, the key is that, esp32 core like idf is also esp32 arduino core, so, using this CMake like reference I get link all files in the core with no copy.

* compilar.sh:
	* change path of the idf and xtensa, to relative of the runtime.platform.path

	* create the idf project (Makefile, CMakeLists.txt, main directory etc....) with the current .ino (hello_world)

* create idfproyect with cmakes in build directory --> createProject.py
  
* When arduino ide create .ino.cpp, add "Arduino.h", so I need to create Arduino component to test --> done