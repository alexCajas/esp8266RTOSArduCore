#ifndef TASKHELLOQ_H
#define TASKHELLOQ_H

#include "Task.h"

/**
 * @brief Manda y recibe un mensaje a TaskWorldQueue.
 * 
 */
class TaskHelloQueue : public Task{
    private:
        
        QueueHandle_t * helloQueue;
        QueueHandle_t * worldQueue;
        

        void run (void * data){
            String fromTaskWorld;
            while(true){

                xQueueReceive((*helloQueue),&fromTaskWorld,portMAX_DELAY);
                Serial.println("TAG: TaskHello: "+fromTaskWorld);
                vTaskDelay(1000);

                String toTaskWorld= "hello from taskHello";
                xQueueSend((*worldQueue),&toTaskWorld,portMAX_DELAY);                
            
            }
        }
    public:
        TaskHelloQueue(QueueHandle_t * helloQueue,QueueHandle_t * worldQueue): Task("TaskHello",1024,TaskPrio_Low){
            this->worldQueue = worldQueue;
            this->helloQueue = helloQueue;
        }

        
};

#endif