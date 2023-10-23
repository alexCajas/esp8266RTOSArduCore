#ifndef COMPONENTS_CPP_UTILS_TASK_H_
#define COMPONENTS_CPP_UTILS_TASK_H_
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include "Arduino.h"



/**
 * @brief Names for Base set of Priorities.
 *
 * Assigns used based names to priority levels, optimized for configMAX_PRIORITIES = 6 for maximal distinctions
 * with reasonable collapsing for smaller values. If configMAX_PRIORITIES is >6 then some values won't have names here, but
 * values could be created and cast to the enum type.
 *
 * | configMAX_PRIORITIES: | 1 | 2 | 3 | 4 | 5 | 6 | N>6 | Use                                                |
 * | --------------------: | - | - | - | - | - | - | :-: | :------------------------------------------------- |
 * | TaskPrio_Idle         | 0 | 0 | 0 | 0 | 0 | 0 |  0  | Non-Real Time operations, Tasks that don't block   |
 * | TaskPrio_Low          | 0 | 1 | 1 | 1 | 1 | 1 |  1  | Non-Critical operations                            |
 * | TaskPrio_HMI          | 0 | 1 | 1 | 1 | 1 | 2 |  2  | Normal User Interface                              |
 * | TaskPrio_Mid          | 0 | 1 | 1 | 2 | 2 | 3 | N/2 | Semi-Critical, Deadlines, not much processing      |
 * | TaskPrio_High         | 0 | 1 | 2 | 3 | 3 | 4 | N-2 | Urgent, Short Deadlines, not much processing       |
 * | TaskPrio_Highest      | 0 | 1 | 2 | 3 | 4 | 5 | N-1 | Critical, do NOW, must be quick (Used by FreeRTOS) |
 *
 */
enum TaskPriority {
	TaskPrio_Idle = 0,													///< Non-Real Time operations. tasks that don't block
	TaskPrio_Low = ((configMAX_PRIORITIES)>1),                         	///< Non-Critical operations
	TaskPrio_HMI = (TaskPrio_Low + ((configMAX_PRIORITIES)>5)),			///< Normal User Interface Level
	TaskPrio_Mid = ((configMAX_PRIORITIES)/2),							///< Semi-Critical, have deadlines, not a lot of processing
	TaskPrio_High = ((configMAX_PRIORITIES)-1-((configMAX_PRIORITIES)>4)), ///< Urgent tasks, short deadlines, not much processing
	TaskPrio_Highest = ((configMAX_PRIORITIES)-1) 						///< Critical Tasks, Do NOW, must be quick (Used by FreeRTOS)
};



/**
 * @brief Encapsulate a runnable task.
 *
 * This class is designed to be subclassed with the method:
 *
 * @code{.cpp}
 * void run(void *data) { ... }
 * @endcode
 *
 * For example:
 *
 * @code{.cpp}
 * class CurlTestTask : public Task {
 *    void run(void *data) {
 *       // Do something
 *    }
 * };
 * 
 * Importante: apesar de que el constructor espera un 
 * const char * taskName, escribir lo siguiente falla:
 * 
  * class CurlTestTask : public Task {
  *   const char *name = "name";
  *   
  *   CurlTestTask(): Task(name,...){}
 *    void run(void *data) {
 *       // Do something
 *    }
 * };
 * 
 * El uso correcto es:
 * class CurlTestTask : public Task {
 *   CurlTestTask(): Task("name",...){}
 *    void run(void *data) {
 *       // Do something
 *    }
 * };
 * @endcode
 *
 * implemented.
 */
class Task {
public:
	Task(const char * taskName = "Task", uint32_t stackSize = 1024, uint8_t priority = TaskPrio_Low);
	virtual ~Task();
	void setStackSize(uint32_t stackSize);
	void setPriority(uint8_t priority);
	void setName(const char * name);
	xTaskHandle getTaskHandle();
	const char* getName();
	void setCore(BaseType_t coreId);
	void start(void* taskData = nullptr);
	void stop();
	/**
	 * @brief Body of the task to execute.
	 *
	 * This function must be implemented in the subclass that represents the actual task to run.
	 * When a task is started by calling start(), this is the code that is executed in the
	 * newly created task.
	 *
	 * @param [in] data The data passed in to the newly started task.
	 */
	virtual void run(void* data) = 0; // Make run pure virtual
	static void delay(int ms);

private:
	xTaskHandle m_handle;
	void*       m_taskData;
	static void runTask(void* data);
	const char* m_taskName;
	uint16_t    m_stackSize;
	uint8_t     m_priority;
	BaseType_t  m_coreId;

};

#endif /* COMPONENTS_CPP_UTILS_TASK_H_ */