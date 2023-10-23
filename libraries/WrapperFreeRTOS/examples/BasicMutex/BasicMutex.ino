/**
 * @file BasicMutex.ino
 * @author Alex Cajas (https://github.com/alexCajas/WrapperFreeRTOS)
 * @brief En este ejemplo, se muestra como coordinar dos hilos,
 * mediante un mutex.
 * 
 * TaskHello, imprime la palabra "Hello", por pantalla.
 * TaskWorld, imprime la palabra "World" por pantalla.
 * @version 0.1
 * 
 */

#include "TaskHello.h"
#include "TaskWorld.h"

TaskHello *taskHello;
TaskWorld *taskWorld;

SemaphoreHandle_t mutexHello;
SemaphoreHandle_t mutexWorld;

void setup(){
    Serial.begin(115200);
    mutexHello = xSemaphoreCreateMutex();  
    mutexWorld = xSemaphoreCreateMutex();

    if(mutexHello == NULL || mutexWorld == NULL ){
        Serial.println("fallo al crear los mutex");
        ESP.restart();
    }

    taskHello = new TaskHello(&mutexHello, &mutexWorld);
    taskWorld = new TaskWorld(&mutexHello, &mutexWorld);

    // set worldMutex to 0;
    xSemaphoreTake(mutexWorld,portMAX_DELAY);

    taskHello->start();
    taskWorld->start();
}

void loop(){
    // tu codigo.
}