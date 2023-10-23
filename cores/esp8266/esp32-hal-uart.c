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

#include "esp32-hal-uart.h"
#include "esp32-hal.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "rom/ets_sys.h"
#include "esp_attr.h"
#include "rom/uart.h"
#include "esp_err.h"
#include "esp_log.h"

#include "esp8266/uart_struct.h"
#include "esp8266/uart_register.h"
#include "esp8266/pin_mux_register.h"
#include "esp8266/eagle_soc.h"

#include "esp8266/rom_functions.h"

#include "rom/ets_sys.h"
#include "driver/uart_select.h"

#define UART_REG_BASE(u)    ((u==0)?DR_REG_UART_BASE:(      (u==1)?DR_REG_UART1_BASE:(    (u==2)?DR_REG_UART2_BASE:0)))
#define UART_RXD_IDX(u)     ((u==0)?U0RXD_IN_IDX:(          (u==1)?U1RXD_IN_IDX:(         (u==2)?U2RXD_IN_IDX:0)))
#define UART_TXD_IDX(u)     ((u==0)?U0TXD_OUT_IDX:(         (u==1)?U1TXD_OUT_IDX:(        (u==2)?U2TXD_OUT_IDX:0)))
#define UART_INTR_SOURCE(u) ((u==0)?ETS_UART0_INTR_SOURCE:( (u==1)?ETS_UART1_INTR_SOURCE:((u==2)?ETS_UART2_INTR_SOURCE:0)))

static int s_uart_debug_nr = 0;

struct uart_struct_t {
    uart_dev_t * dev;
#if !CONFIG_DISABLE_HAL_LOCKS
    xSemaphoreHandle lock;
#endif
    uint8_t num;
    xQueueHandle queue;
    void (*intr_handle)(void);
};

#if CONFIG_DISABLE_HAL_LOCKS
#define UART_MUTEX_LOCK()
#define UART_MUTEX_UNLOCK()

static uart_t _uart_bus_array[2] = {
    {(volatile uart_dev_t *)0x60000000, NULL, 0, NULL, NULL},
    {(volatile uart_dev_t *)0x60000F00, NULL, 1, NULL, NULL},
};
#else
#define UART_MUTEX_LOCK()    do {} while (xSemaphoreTake(uart->lock, portMAX_DELAY) != pdPASS)
#define UART_MUTEX_UNLOCK()  xSemaphoreGive(uart->lock)

static uart_t _uart_bus_array[2] = {
    {(volatile uart_dev_t *)0x60000000, NULL, 0, NULL, NULL},
    {(volatile uart_dev_t *)0x60000F00, NULL, 1, NULL, NULL},
};
#endif


/**
 * @brief isr handler
 * 
 * @param arg 
 */
static void IRAM_ATTR _uart_isr(void *arg)
{
    uint8_t i, c;
    BaseType_t xHigherPriorityTaskWoken;
    uart_t* uart;

    for (i = 0; i < UART_NUM_MAX; i++) {
        uart = &_uart_bus_array[i];

        if (uart->intr_handle == NULL) {
            continue;
        }

        uint32_t intr_status = uart->dev->int_st.val;
        if (intr_status != 0) {
            uart->dev->int_clr.val = intr_status;
            if (intr_status & UART_RXFIFO_FULL_INT_ST) {
                while (uart->dev->status.rxfifo_cnt) {
                    c = uart->dev->fifo.rw_byte;
                    if (uart->queue != NULL) {
                        xQueueSendFromISR(uart->queue, &c, &xHigherPriorityTaskWoken);
                    }
                }
            }
        }
    }

    if (xHigherPriorityTaskWoken) {
        portYIELD_FROM_ISR();
    }
}

void uartEnableInterrupt(uart_t* uart)
{
    uart_enable_rx_intr(uart->num);
}

void uartDisableInterrupt(uart_t* uart)
{
    uart_disable_rx_intr(uart->num);
}

void uartDetachRx(uart_t* uart, uint8_t rxPin)
{
    if(uart == NULL) {
        return;
    }
    uartDisableInterrupt(uart);
}

void uartDetachTx(uart_t* uart, uint8_t txPin)
{
    if(uart == NULL) {
        return;
    }
    uart_disable_tx_intr(uart->num);
}

void uartAttachRx(uart_t* uart, uint8_t rxPin, bool inverted)
{
    if(uart == NULL) {
        return;
    }
    pinMode(rxPin, INPUT);
    uartEnableInterrupt(uart);
}

void uartAttachTx(uart_t* uart, uint8_t txPin, bool inverted)
{
    if(uart == NULL) {
        return;
    }
    pinMode(txPin, OUTPUT);
}

uart_t* uartBegin(uint8_t uart_nr, uint32_t baudrate, uint32_t config, int8_t rxPin, int8_t txPin, uint16_t queueLen, bool inverted) {
    if (uart_nr >= UART_NUM_MAX) {
        return NULL;
    }
    
    if (rxPin == -1 && txPin == -1) {
        return NULL;
    }
    
    uart_t* uart = &_uart_bus_array[uart_nr];

#if !CONFIG_DISABLE_HAL_LOCKS
    if (uart->lock == NULL) {
        uart->lock = xSemaphoreCreateMutex();
        if (uart->lock == NULL) {
            return NULL;
        }
    }
#endif

    if (queueLen && uart->queue == NULL) {
        uart->queue = xQueueCreate(queueLen, sizeof(uint8_t));
        if (uart->queue == NULL) {
            return NULL;
        }
    }

    // communication pins and install the driver
    uart_config_t uart_config = {
        .baud_rate = baudrate,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE
    };
    uart_param_config(uart_nr, &uart_config);
    uartFlush(uart);

    UART_MUTEX_LOCK();
    uart->dev->conf0.val = config;
    #define TWO_STOP_BITS_CONF 0x3
    #define ONE_STOP_BITS_CONF 0x1

    if (uart->dev->conf0.stop_bit_num == TWO_STOP_BITS_CONF) {
        uart->dev->conf0.stop_bit_num = ONE_STOP_BITS_CONF;
        
    }

    UART_MUTEX_UNLOCK();

    if (rxPin != -1) {
        uartAttachRx(uart, rxPin, inverted);
    }

    if (txPin != -1) {
        uartAttachTx(uart, txPin, inverted);
    }

    return uart;
}


void uartEnd(uart_t* uart, uint8_t txPin, uint8_t rxPin)
{
    if(uart == NULL) {
        return;
    }

    UART_MUTEX_LOCK();
    if(uart->queue != NULL) {
        vQueueDelete(uart->queue);
        uart->queue = NULL;
    }

    uart->dev->conf0.val = 0;

    UART_MUTEX_UNLOCK();

    uartDetachRx(uart, rxPin);
    uartDetachTx(uart, txPin);
}

size_t uartResizeRxBuffer(uart_t * uart, size_t new_size) {
    if(uart == NULL) {
        return 0;
    }

    UART_MUTEX_LOCK();
    if(uart->queue != NULL) {
        vQueueDelete(uart->queue);
        uart->queue = xQueueCreate(new_size, sizeof(uint8_t));
        if(uart->queue == NULL) {
            UART_MUTEX_UNLOCK();
            return 0;
        }
    }
    UART_MUTEX_UNLOCK();

    return new_size;
}

void uartSetRxInvert(uart_t* uart, bool invert)
{
    if (uart == NULL)
        return;
    
    if (invert)
        uart->dev->conf0.rxd_inv = 1;
    else
        uart->dev->conf0.rxd_inv = 0;
}

uint32_t uartAvailable(uart_t* uart)
{
    if(uart == NULL || uart->queue == NULL) {
        return 0;
    }
    return (uxQueueMessagesWaiting(uart->queue) + uart->dev->status.rxfifo_cnt) ;
}

uint32_t uartAvailableForWrite(uart_t* uart)
{
    if(uart == NULL) {
        return 0;
    }
    return 0x7f - uart->dev->status.txfifo_cnt;
}

void uartRxFifoToQueue(uart_t* uart)
{
	uint8_t c;
    UART_MUTEX_LOCK();
	//disable interrupts
	uart->dev->int_ena.val = 0;
	uart->dev->int_clr.val = 0xffffffff;
        uint32_t intr_status = uart->dev->int_st.val;
        if (intr_status != 0) {
            uart->dev->int_clr.val = intr_status;
            if (intr_status & UART_RXFIFO_FULL_INT_ST) {
                while (uart->dev->status.rxfifo_cnt) {
                    c = uart->dev->fifo.rw_byte;
                    if (uart->queue != NULL) {
                        xQueueSend(uart->queue, &c, 0);
                    }
                }
            }
        }
	//enable interrupts
	uart->dev->int_ena.rxfifo_full = 1;
	uart->dev->int_ena.frm_err = 1;
	uart->dev->int_ena.rxfifo_tout = 1;
	uart->dev->int_clr.val = 0xffffffff;
    UART_MUTEX_UNLOCK();
}

uint8_t uartRead(uart_t* uart)
{
    if(uart == NULL || uart->queue == NULL) {
        return 0;
    }
    uint8_t c;
    if ((uxQueueMessagesWaiting(uart->queue) == 0) && (uart->dev->status.rxfifo_cnt > 0))
    {
    	uartRxFifoToQueue(uart);
    }
    if(xQueueReceive(uart->queue, &c, 0)) {
        return c;
    }
    return 0;
}

uint8_t uartPeek(uart_t* uart)
{
    if(uart == NULL || uart->queue == NULL) {
        return 0;
    }
    uint8_t c;
    if ((uxQueueMessagesWaiting(uart->queue) == 0) && (uart->dev->status.rxfifo_cnt > 0))
    {
    	uartRxFifoToQueue(uart);
    }
    if(xQueuePeek(uart->queue, &c, 0)) {
        return c;
    }
    return 0;
}

void uartWrite(uart_t* uart, uint8_t c)
{
    if(uart == NULL) {
        return;
    }
    UART_MUTEX_LOCK();
    while(uart->dev->status.txfifo_cnt == 0x7F);
    uart->dev->fifo.rw_byte = c;
    UART_MUTEX_UNLOCK();
}

void uartWriteBuf(uart_t* uart, const uint8_t * data, size_t len)
{
    if(uart == NULL) {
        return;
    }
    UART_MUTEX_LOCK();
    while(len) {
        while(uart->dev->status.txfifo_cnt == 0x7F);
        uart->dev->fifo.rw_byte = *data++;
        len--;
    }
    UART_MUTEX_UNLOCK();
}

void uartFlush(uart_t* uart)
{
    uartFlushTxOnly(uart,true);
}

void uartFlushTxOnly(uart_t* uart, bool txOnly)
{
    if(uart == NULL) {
        return;
    }

    UART_MUTEX_LOCK();
    uart_wait_tx_done(uart->num, 1000);  // Espera a que se transmita todo
    
    if( !txOnly ){
        //Due to hardware issue, we can not use fifo_rst to reset uart fifo.
        //See description about UART_TXFIFO_RST and UART_RXFIFO_RST in <<esp32_technical_reference_manual>> v2.6 or later.

        // we read the data out and make `fifo_len == 0 && rd_addr == wr_addr`.
        uart_flush_input(uart->num);
        xQueueReset(uart->queue);
    }
    
    UART_MUTEX_UNLOCK();
}

void uartSetBaudRate(uart_t* uart, uint32_t baud_rate)
{
    if(uart == NULL) {
        return;
    }
    UART_MUTEX_LOCK();
    uart_set_baudrate(uart->num,baud_rate);
    UART_MUTEX_UNLOCK();
}


uint32_t uartGetBaudRate(uart_t* uart)
{
    if(uart == NULL) {
        return 0;
    }

    uint32_t baud = -1;
    uart_get_baudrate(uart->num,&baud);
    return baud;
}

static void IRAM_ATTR uart0_write_char(char c)
{
    char buffer[1];
    buffer[0] = c ;
    uart_write_bytes(UART_NUM_0,buffer,1);
}

static void IRAM_ATTR uart1_write_char(char c)
{
    char buffer[1];
    buffer[0] = c ;
    uart_write_bytes(UART_NUM_1,buffer,1);
}



void uart_install_putc()
{
    switch(s_uart_debug_nr) {
    case 0:
        os_install_putc1((void (*)(char)) &uart0_write_char);
        break;
    case 1:
        os_install_putc1((void (*)(char)) &uart1_write_char);
        break;
    default:
        os_install_putc1(NULL);
        break;
    }
}

void uartSetDebug(uart_t* uart)
{
    if(uart == NULL || uart->num > UART_NUM_MAX) {
        s_uart_debug_nr = -1;
        //ets_install_putc1(NULL);
        //return;
    } else
    if(s_uart_debug_nr == uart->num) {
        return;
    } else
    s_uart_debug_nr = uart->num;
    uart_install_putc();
}

int uartGetDebug()
{
    return s_uart_debug_nr;
}

int log_printf(const char *format, ...)
{
    if(s_uart_debug_nr < 0){
        return 0;
    }
    static char loc_buf[64];
    char * temp = loc_buf;
    int len;
    va_list arg;
    va_list copy;
    va_start(arg, format);
    va_copy(copy, arg);
    len = vsnprintf(NULL, 0, format, arg);
    va_end(copy);
    if(len >= sizeof(loc_buf)){
        temp = (char*)malloc(len+1);
        if(temp == NULL) {
            return 0;
        }
    }
    vsnprintf(temp, len+1, format, arg);
#if !CONFIG_DISABLE_HAL_LOCKS
    if(_uart_bus_array[s_uart_debug_nr].lock){
        xSemaphoreTake(_uart_bus_array[s_uart_debug_nr].lock, portMAX_DELAY);
        ets_printf("%s", temp);
        xSemaphoreGive(_uart_bus_array[s_uart_debug_nr].lock);
    } else {
        ets_printf("%s", temp);
    }
#else
    ets_printf("%s", temp);
#endif
    va_end(arg);
    if(len >= sizeof(loc_buf)){
        free(temp);
    }
    return len;
}

/*
 * if enough pulses are detected return the minimum high pulse duration + minimum low pulse duration divided by two. 
 * This equals one bit period. If flag is true the function return inmediately, otherwise it waits for enough pulses.
 */
unsigned long uartBaudrateDetect(uart_t *uart, bool flg)
{
    while(uart->dev->rxd_cnt.edge_cnt < 30) { // UART_PULSE_NUM(uart_num)
        if(flg) return 0;
        ets_delay_us(1000);
    }

    UART_MUTEX_LOCK();
    unsigned long ret = ((uart->dev->lowpulse.min_cnt + uart->dev->highpulse.min_cnt) >> 1) + 12;
    UART_MUTEX_UNLOCK();

    return ret;
}

/*
 * To start detection of baud rate with the uart the auto_baud.en bit needs to be cleared and set. The bit period is 
 * detected calling uartBadrateDetect(). The raw baudrate is computed using the UART_CLK_FREQ. The raw baudrate is 
 * rounded to the closed real baudrate.
*/
void uartStartDetectBaudrate(uart_t *uart) {
  if(!uart) return;

  uart->dev->auto_baud.glitch_filt = 0x08;
  uart->dev->auto_baud.en = 0;
  uart->dev->auto_baud.en = 1;
}

unsigned long
uartDetectBaudrate(uart_t *uart)
{
    static bool uartStateDetectingBaudrate = false;

    if(!uartStateDetectingBaudrate) {
        uart->dev->auto_baud.glitch_filt = 0x08;
        uart->dev->auto_baud.en = 0;
        uart->dev->auto_baud.en = 1;
        uartStateDetectingBaudrate = true;
    }

    unsigned long divisor = uartBaudrateDetect(uart, true);
    if (!divisor) {
        return 0;
    }

    uart->dev->auto_baud.en = 0;
    uartStateDetectingBaudrate = false; // Initialize for the next round

    unsigned long baudrate = getApbFrequency() / divisor;

    static const unsigned long default_rates[] = {300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 74880, 115200, 230400, 256000, 460800, 921600, 1843200, 3686400};

    size_t i;
    for (i = 1; i < sizeof(default_rates) / sizeof(default_rates[0]) - 1; i++)	// find the nearest real baudrate
    {
        if (baudrate <= default_rates[i])
        {
            if (baudrate - default_rates[i - 1] < default_rates[i] - baudrate) {
                i--;
            }
            break;
        }
    }

    return default_rates[i];
}


