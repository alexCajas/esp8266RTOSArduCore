#ifndef TASKCONSUMMER_H
#define TASKCONSUMMER_H

#include "Task.h"

/**
 * @brief Ejemplo de coordinación entre consumidores rapidos
 * y productor lento.
 * 
 */
class TaskConsummer : public Task{
    private:
        
        SemaphoreHandle_t * semaphore;
        int id;

        void run (void * data){
            while(true){
                xSemaphoreTake((*semaphore),portMAX_DELAY);
                Serial.print("Hello from task ");
                vTaskDelay(300);
                Serial.println(id);
            }
        }
    public:
        TaskConsummer(SemaphoreHandle_t * semaphore, int id): Task("TaskConsummer",1024,TaskPrio_Low){
            this->semaphore = semaphore;
            this->id = id;
        }

        
};

#endif //TASKCONSUMMER_H