# WrapperFreeRTOS

**FreeRTOS C++ Wrapper** para el fácil uso de las principales utilidades de concurrencia, de FreeRTOS, en **POO**, compatible con **Arduino core** y probado en un **ESP32**.

Está basado en los wrappers de **Neil Kolban** [https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/Task.cpp], y **Richard Damon** [https://github.com/richard-damon/FreeRTOScpp/blob/master/TaskCPP.h] .

---

## Ejemplos:

* **BasicTask:** Creación de un objecto concurrente.

* **BasicMutex:** Coordinación entre dos objetos concurrentes mediante mutex o semáforo binario.     

* **BasicSemaphore:** Típico problema un productor lento y varios consumidores rápidos, resuelto mediante un "counting semaphore".

* **BasicQueue:** Envío de datos mediante QueueHandle_t entre dos objetos concurrentes.  

* **CrossedReferences:** Ejemplo de una posible solución entre referencias cruzadas de objetos en C++.

---

## Adaptacion de wrappers

* La adaptación del wrapper Task.h y Task.cpp (nKolban), consitió en sustituir la libreria  std::string por Arduino.h, y redefinir toda variable y argumento tipo std::string u otros std:: por su conrrespondiente en Arduino.h, notar que se adapta según los parámetros pasados a las funciones de creación y manipulación de TaskHandle_t.

* Se sustituye el valor de stack size de uint8 a uint32, puesto que xcreateTask() recibe un unit32. 

* Se añade un enum (TaskPriority) que recoge el valor númerico de las distintas prioridades predefinidas en la versión de FreeRTOS usada en tu proyecto (Richard Damon).

* Se añade el método xTaskHandle getTaskHandle(). 

---

## Bibliografía

* [https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/Task.cpp]

* [https://github.com/richard-damon/FreeRTOScpp/blob/master/TaskCPP.h]


---

## Licencia
* MIT License
