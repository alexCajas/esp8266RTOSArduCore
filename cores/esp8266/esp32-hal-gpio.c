// Copyright 2015-2016 Espressif Systems (Shanghai) PTE LTD
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "esp32-hal-gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "rom/ets_sys.h"
#include "esp_attr.h"

#include "rom/gpio.h"
#include "driver/gpio.h"
#include "esp_err.h"
#include "esp_log.h"
#include "esp_system.h"

typedef void (*voidFuncPtr)(void);
typedef void (*voidFuncPtrArg)(void*);

extern void IRAM_ATTR __pinMode(uint8_t pin, uint8_t mode)
{
    switch (mode)
    {
    case INPUT:
        gpio_set_direction(pin,GPIO_MODE_INPUT);
        break;
    
    case INPUT_PULLUP:
        gpio_set_direction(pin,GPIO_MODE_INPUT);
        gpio_set_pull_mode(pin,GPIO_PULLUP_ONLY);
        gpio_pullup_en(pin);
    break;

    case OUTPUT:
        gpio_set_direction(pin,GPIO_MODE_OUTPUT);
        break;

    case OUTPUT_OPEN_DRAIN:
        gpio_set_direction(pin,GPIO_MODE_OUTPUT_OD);
        break;

    case INPUT_PULLDOWN_16:
        gpio_set_direction(pin,GPIO_MODE_INPUT);
        gpio_set_pull_mode(pin,GPIO_PULLDOWN_ONLY);
        gpio_pulldown_en(pin);        
        break;

    default:
        break;
    }
 
}

extern void IRAM_ATTR __digitalWrite(uint8_t pin, uint8_t val)
{
    gpio_set_level(pin,val);
}

extern int IRAM_ATTR __digitalRead(uint8_t pin)
{
    return gpio_get_level(pin);
}


extern void cleanupFunctional(void* arg);

extern void __attachInterruptFunctionalArg(uint8_t pin, voidFuncPtrArg userFunc, void * arg, int intr_type, bool functional)
{
    gpio_set_intr_type(pin,intr_type);
    gpio_install_isr_service(0); // necesary to install irs service, "0" is dummy value, only used in esp32
    gpio_isr_handler_add(pin, userFunc, arg);
}

extern void __attachInterruptArg(uint8_t pin, voidFuncPtrArg userFunc, void * arg, int intr_type)
{
	__attachInterruptFunctionalArg(pin, userFunc, arg, intr_type, false);
}

extern void __attachInterrupt(uint8_t pin, voidFuncPtr userFunc, int intr_type) {
    __attachInterruptFunctionalArg(pin, (voidFuncPtrArg)userFunc, NULL, intr_type, false);
}

extern void __detachInterrupt(uint8_t pin)
{
    gpio_isr_handler_remove(pin);
}


extern void pinMode(uint8_t pin, uint8_t mode) __attribute__ ((weak, alias("__pinMode")));
extern void digitalWrite(uint8_t pin, uint8_t val) __attribute__ ((weak, alias("__digitalWrite")));
extern int digitalRead(uint8_t pin) __attribute__ ((weak, alias("__digitalRead")));
extern void attachInterrupt(uint8_t pin, voidFuncPtr handler, int mode) __attribute__ ((weak, alias("__attachInterrupt")));
extern void attachInterruptArg(uint8_t pin, voidFuncPtrArg handler, void * arg, int mode) __attribute__ ((weak, alias("__attachInterruptArg")));
extern void detachInterrupt(uint8_t pin) __attribute__ ((weak, alias("__detachInterrupt")));

