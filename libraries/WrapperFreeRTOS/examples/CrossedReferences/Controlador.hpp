#ifndef CONTROLADOR_HPP
#define CONTROLADOR_HPP

#include "Task.h"
/**
 * @brief Ejemplo para resolver el problema de la referencia 
 * Cruzada en c++.
 * 
 */

class ThreadTask;

/**
 * @brief Controlador tiene una referencia a ThreadTask.
 * 
 */
class Controlador {
    private:
        ThreadTask *thread;
        String nombre;
    public:
        Controlador(String nombre);
        
        /**
         * @brief pone en funcionamiento al hilo.
         * 
         */
        void start();
        
        String getNombre(){
            return nombre;
        }
};

/**
 * @brief ThreadTask curza su referencia con Controlador
 * al tenerlo como atributo.
 * 
 */
class ThreadTask : public Task{

    private:
        Controlador *controlador;

        /**
         * @brief Override de la función que hará 
         * La tarea en bucle.
         * 
         * @param data 
         */
        void run(void *data);

    public:
        ThreadTask(Controlador* controlador);
    
};

#endif //CONTROLADOR_HPP