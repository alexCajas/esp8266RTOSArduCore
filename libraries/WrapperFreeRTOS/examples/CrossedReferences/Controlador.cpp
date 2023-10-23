#include "Controlador.hpp"

Controlador::Controlador(String nombre){
    this->nombre = nombre;
    this->thread = new ThreadTask(this);

    // no empiezes la tarea en el constructor
    // da fallo de memoria. Por eso se crea el
    // metodo Controlador::start();
}


void Controlador::start(){
    // uso correcto. 
    thread->start();
}

/**************** ThreadTask ******************/
ThreadTask::ThreadTask(Controlador * controlador):Task("ThreadTask",1024,TaskPrio_Low){
    this->controlador = controlador;
}

void ThreadTask::run(void * data){
    while(true){
        Serial.println(controlador->getNombre());
        vTaskDelay(1000);
    }
}