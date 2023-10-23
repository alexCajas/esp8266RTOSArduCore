/**
 * @file BasicSemaphore.ino
 * @author Alex Cajas (https://github.com/alexCajas/)
 * @brief Ejemplo de coordinación entre consumidores rápidos
 * y productor lento. 
 * @version 0.1
 * 
 */

#include "TaskConsummer.hpp"
#include "TaskProducer.hpp"

TaskConsummer *consummer;
TaskProducer * producer;

SemaphoreHandle_t semaphore;

void setup(){
    Serial.begin(115200);
    semaphore = xSemaphoreCreateCounting( 5, 0 ); 

    if(semaphore == NULL ){
        Serial.println("fallo al crear el semaphore");
        ESP.restart();
    }

    for (int i = 0; i < 10; i++){
        consummer = new TaskConsummer(&semaphore, i);
        consummer->start();
    }

    producer = new TaskProducer(&semaphore);
    producer->start();

}   

void loop(){
    // tu codigo.
}