#ifndef TASKPRODUCER_H
#define TASKPRODUCER_H

 #include "Task.h"

/**
 * @brief Ejemplo de coordinación entre consumidores rapidos
 * y productor lento.
 */
class TaskProducer : public Task{
    private:
        SemaphoreHandle_t * semaphore;
        int id;

        void run (void * data){
            while(true){
                vTaskDelay(1000);
                xSemaphoreGive((*semaphore));
            }
        }
    public:
        TaskProducer(SemaphoreHandle_t * semaphore): Task("TaskProducer",1024,TaskPrio_Low){
            this->semaphore = semaphore;
        }

        
};

#endif //TASKPRODUCER_H