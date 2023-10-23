#ifndef TASKWORLD_H
#define TASKWORLD_H

 #include "Task.h"

/**
 * @brief Imprimer la palabra "World" por pantalla
 * 
 */
class TaskWorld : public Task{
    private:
        SemaphoreHandle_t * helloMutex;
        SemaphoreHandle_t * worldMutex;

        void run (void * data){
            while(true){
                xSemaphoreTake((*worldMutex),portMAX_DELAY);
                Serial.println("world");
                vTaskDelay(1000);
                xSemaphoreGive((*helloMutex));
            }
        }
    public:
        TaskWorld(SemaphoreHandle_t * helloMutex,SemaphoreHandle_t *worldMutex): Task("TaskWorld",1024,TaskPrio_Low){
            this->worldMutex = worldMutex;
            this->helloMutex = helloMutex;
        }

        
};

#endif