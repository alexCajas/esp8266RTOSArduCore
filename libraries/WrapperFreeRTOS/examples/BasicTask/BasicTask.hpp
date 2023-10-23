#ifndef BASICTASK_HPP
#define BASICTASK_HPP

#include "Task.h"
/**
 * @brief Objeto que hereda de Task, debe implementar el método
 * run, además notar que el constructor Task, recibe un "",
 * apesar de que está definido para recibir un const char* TaskName,
 * pasar una variable como const char * name = "nombre";
 * al constructor como por ejemplo:
 * SomeClass(const char* name):Task(name,...) 
 * da fallo de loadException. 
 * Uso correcto en el constructor de Task:
 * Task("nombre",...)
 */
class BasicTask : public Task{
    public:
        BasicTask();
        // override la función de la interfaz Task. 
        void run (void *data);
};

#endif //BASICTASK_H