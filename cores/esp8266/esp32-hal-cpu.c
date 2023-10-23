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

#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "freertos/task.h"
#include "freertos/xtensa_timer.h"
#include "esp_attr.h"
#include "esp_log.h"
#include "driver/rtc.h"
#include "esp_clk.h"
#include "esp_timer.h"

#include "esp_system.h"
#include "esp32-hal-cpu.h"
#include "esp32-hal.h"

const uint32_t MHZ = 1000000;


/* in esp8266 the freq of APB is fixed to 80MHZ, so it is no needed get from conf->freq_mhz to 80

#if CONFIG_IDF_TARGET_ESP32 

typedef struct apb_change_cb_s {
        struct apb_change_cb_s * prev;
        struct apb_change_cb_s * next;
        void * arg;
        apb_change_cb_t cb;
} apb_change_t;



static apb_change_t * apb_change_callbacks = NULL;
static xSemaphoreHandle apb_change_lock = NULL;

static void initApbChangeCallback(){
    static volatile bool initialized = false;
    if(!initialized){
        initialized = true;
        apb_change_lock = xSemaphoreCreateMutex();
        if(!apb_change_lock){
            initialized = false;
        }
    }
}

static void triggerApbChangeCallback(apb_change_ev_t ev_type, uint32_t old_apb, uint32_t new_apb){
    initApbChangeCallback();
    xSemaphoreTake(apb_change_lock, portMAX_DELAY);
    apb_change_t * r = apb_change_callbacks;
    if( r != NULL ){
        if(ev_type == APB_BEFORE_CHANGE )
            while(r != NULL){
                r->cb(r->arg, ev_type, old_apb, new_apb);
                r=r->next;
            }
        else { // run backwards through chain
            while(r->next != NULL) r = r->next; // find first added
            while( r != NULL){
                r->cb(r->arg, ev_type, old_apb, new_apb);
                r=r->prev;
            }
        }
    }
    xSemaphoreGive(apb_change_lock);
}

bool addApbChangeCallback(void * arg, apb_change_cb_t cb){
    initApbChangeCallback();
    apb_change_t * c = (apb_change_t*)malloc(sizeof(apb_change_t));
    if(!c){
        log_e("Callback Object Malloc Failed");
        return false;
    }
    c->next = NULL;
    c->prev = NULL;
    c->arg = arg;
    c->cb = cb;
    xSemaphoreTake(apb_change_lock, portMAX_DELAY);
    if(apb_change_callbacks == NULL){
        apb_change_callbacks = c;
    } else {
        apb_change_t * r = apb_change_callbacks;
        // look for duplicate callbacks
        while( (r != NULL ) && !((r->cb == cb) && ( r->arg == arg))) r = r->next;
        if (r) {
            log_e("duplicate func=%08X arg=%08X",c->cb,c->arg);
            free(c);
            xSemaphoreGive(apb_change_lock);
            return false;
        }
        else {
            c->next = apb_change_callbacks;
            apb_change_callbacks-> prev = c;
            apb_change_callbacks = c;
        }
    }
    xSemaphoreGive(apb_change_lock);
    return true;
}

bool removeApbChangeCallback(void * arg, apb_change_cb_t cb){
    initApbChangeCallback();
    xSemaphoreTake(apb_change_lock, portMAX_DELAY);
    apb_change_t * r = apb_change_callbacks;
    // look for matching callback
    while( (r != NULL ) && !((r->cb == cb) && ( r->arg == arg))) r = r->next;
    if ( r == NULL ) {
        log_e("not found func=%08X arg=%08X",cb,arg);
        xSemaphoreGive(apb_change_lock);
        return false;
        }
    else {
        // patch links
        if(r->prev) r->prev->next = r->next;
        else { // this is first link
           apb_change_callbacks = r->next;
        }
        if(r->next) r->next->prev = r->prev;
        free(r);
    }
    xSemaphoreGive(apb_change_lock);
    return true;
}



static uint32_t calculateApb(rtc_cpu_freq_config_t * conf){
    if(conf->freq_mhz >= 80){
        return 80 * MHZ;
    }
    return (conf->source_freq_mhz * MHZ) / conf->div;
}

void esp_timer_impl_update_apb_freq(uint32_t apb_ticks_per_us); //private in IDF

#endif
*/

bool setCpuFrequencyMhz(uint32_t cpu_freq){
    

    esp_cpu_freq_t freq = ESP_CPU_FREQ_160M;

    if(cpu_freq != 160 && cpu_freq != 80 ){
        log_e("Frequency %d is not supported.",cpu_freq);
        return false;
    }

    uint32_t currentFreq = getCpuFrequencyMhz();
    if (currentFreq == cpu_freq ){
        log_e("Frequency is already %d\n",cpu_freq);
        return false;
    }

    if (cpu_freq == 80){
        freq = ESP_CPU_FREQ_80M;
    }

    esp_set_cpu_freq(cpu_freq);
    log_i("Started change to %d. It may take several hundred microseconds to perform frequency switch\n",cpu_freq);
    return true;
}

uint32_t getCpuFrequencyMhz(){

    return (esp_clk_cpu_freq()/MHZ);
}

/**
 * @brief Get the Xtal Frequency Mhz object. This value is 
 * getted from:
 * @link https://www.espressif.com/sites/default/files/documentation/esp8266-technical_reference_en.pdf
 * 
 * @return uint32_t 
 */
uint32_t getXtalFrequencyMhz(){
    uint32_t CRYSTAL_FREQ = 26;
    return CRYSTAL_FREQ;
}


uint32_t getApbFrequency(){
    uint32_t freq = (80*MHZ);
    return freq;
}