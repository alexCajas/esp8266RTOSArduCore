/**
 * @file BasicTask.ino
 * @author Alex Cajas (https://github.com/alexCajas/)
 * @brief Ejemplo básico de creación de una clase Task.
 * @version 0.1
 * 
 */

#include "BasicTask.hpp"


BasicTask task;

void setup(){

Serial.begin(115200);
task.start();

}

void loop(){

    // Puedes parar la tarea con
    // task.stop();

    // o puedes suspender su actual ejecución con
    // vTaskSuspend(task.getTaskHandle());
}

