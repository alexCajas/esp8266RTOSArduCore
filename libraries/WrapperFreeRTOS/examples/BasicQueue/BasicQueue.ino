/**
 * @file BasicQeueue.ino
 * @author Alex Cajas (https://github.com/alexCajas/WrapperFreeRTOS)
 * @brief En este ejemplo, se muestra como coordinar dos hilos,
 * y pasar mensajes, mediante un mutex.
 * TaskHello, recibe mensaje de TaskWorldQueue y lo imprime por pantalla.
 * TaskWorld, recibe mensaje de TaskHelloQueue", y lo imprime por pantalla.
 * @version 0.1
 * 
 */

#include "TaskHelloQ.h"
#include "TaskWorldQ.h"

TaskHelloQueue *taskHello;
TaskWorldQueue *taskWorld;

QueueHandle_t queueHello;
QueueHandle_t queueWorld;

void setup(){
    Serial.begin(115200);
    queueHello = xQueueCreate( 1, sizeof(String) );  
    queueWorld = xQueueCreate( 1, sizeof(String));

    if(queueHello == NULL || queueWorld == NULL ){
        Serial.println("fallo al crear los queue");
        ESP.restart();
    }

    taskHello = new TaskHelloQueue(&queueHello, &queueWorld);
    taskWorld = new TaskWorldQueue(&queueHello, &queueWorld);

    taskHello->start();
    taskWorld->start();
}

void loop(){
    // tu codigo.
}