/**
 * @file WrapperFreeRTOS.ino
 * @author Alex Cajas (https://github.com/alexCajas/)
 * @brief Basic example of concurrent Class.
 * @see WrapperFreeRTOS library (https://github.com/alexCajas/WrapperFreeRTOS), for more examples
 * 
 */



#include "Task.h"
#define LED_BUILTIN 2

class BasicTaskBlink : public Task{
    public:
        BasicTaskBlink(){}
        // override la función de la interfaz Task. 
        void run (void *data){
          while(true){
            digitalWrite(LED_BUILTIN, HIGH); // turn the LED on (HIGH is the voltage level)
            vTaskDelay(pdMS_TO_TICKS(500));
            digitalWrite(LED_BUILTIN, LOW); // turn the LED off by making the voltage LOW
            vTaskDelay(pdMS_TO_TICKS(500));                   
          }
        }
};

class BasicTaskHello : public Task{
    public:
        BasicTaskHello(){}
        // override la función de la interfaz Task. 
        void run (void *data){
          while (true){
            Serial.println("Hello from task!");
            vTaskDelay(pdMS_TO_TICKS(1000)); // print hello each 1 sec.       
          }

        }
};


BasicTaskBlink taskBlink;
BasicTaskHello taskHello;

void setup(){

  Serial.begin(115200);
  taskBlink.start();
  taskHello.start();


}

void loop(){

    // You can stop task 
    // taskBlink.stop();

    // or suspend it
    // vTaskSuspend(taskBlink.getTaskHandle());
}

