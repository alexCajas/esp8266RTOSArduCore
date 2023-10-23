#ifndef TASKWORLDQ_H
#define TASKWORLDQ_H

 #include "Task.h"

/**
 * @brief Manda y recibe un mensaje de TaskHelloQueue 
 * 
 * 
 */
class TaskWorldQueue : public Task{
    private:
        QueueHandle_t * helloQueue;
        QueueHandle_t * worldQueue;

        void run (void * data){
            String fromTaskHello;
            while(true){
                String toTaskHello= "hello from taskWorld";
                xQueueSend((*helloQueue),&toTaskHello,portMAX_DELAY);                
                
                xQueueReceive((*worldQueue),&fromTaskHello,portMAX_DELAY);
                Serial.println("TAG: TaskWorld: "+fromTaskHello);
                vTaskDelay(1000);
            }
        }
    public:
        TaskWorldQueue(QueueHandle_t * helloQueue,QueueHandle_t * worldQueue): Task("TaskWorld",1024,TaskPrio_Low){
            this->worldQueue = worldQueue;
            this->helloQueue = helloQueue;
        }

        
};

#endif