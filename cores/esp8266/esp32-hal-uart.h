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

#ifndef MAIN_ESP32_HAL_UART_H_
#define MAIN_ESP32_HAL_UART_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>

#define UART0    0
#define UART1    1
#define UART_NO -1

// Options for `config` argument of uart_init
#define UART_NB_BIT_MASK      0B00001100
#define UART_NB_BIT_5         0B00000000
#define UART_NB_BIT_6         0B00000100
#define UART_NB_BIT_7         0B00001000
#define UART_NB_BIT_8         0B00001100

#define UART_PARITY_MASK      0B00000011
#define UART_PARITY_NONE      0B00000000



#define UART_NB_STOP_BIT_MASK 0B00110000
#define UART_NB_STOP_BIT_0    0B00000000
#define UART_NB_STOP_BIT_1    0B00010000
#define UART_NB_STOP_BIT_15   0B00100000
#define UART_NB_STOP_BIT_2    0B00110000

#define UART_5N1 ( UART_NB_BIT_5 | UART_PARITY_NONE | UART_NB_STOP_BIT_1 )
#define UART_6N1 ( UART_NB_BIT_6 | UART_PARITY_NONE | UART_NB_STOP_BIT_1 )
#define UART_7N1 ( UART_NB_BIT_7 | UART_PARITY_NONE | UART_NB_STOP_BIT_1 )
#define UART_8N1 ( UART_NB_BIT_8 | UART_PARITY_NONE | UART_NB_STOP_BIT_1 )
#define UART_5N2 ( UART_NB_BIT_5 | UART_PARITY_NONE | UART_NB_STOP_BIT_2 )
#define UART_6N2 ( UART_NB_BIT_6 | UART_PARITY_NONE | UART_NB_STOP_BIT_2 )
#define UART_7N2 ( UART_NB_BIT_7 | UART_PARITY_NONE | UART_NB_STOP_BIT_2 )
#define UART_8N2 ( UART_NB_BIT_8 | UART_PARITY_NONE | UART_NB_STOP_BIT_2 )
#define UART_5E1 ( UART_NB_BIT_5 | UART_PARITY_EVEN | UART_NB_STOP_BIT_1 )
#define UART_6E1 ( UART_NB_BIT_6 | UART_PARITY_EVEN | UART_NB_STOP_BIT_1 )
#define UART_7E1 ( UART_NB_BIT_7 | UART_PARITY_EVEN | UART_NB_STOP_BIT_1 )
#define UART_8E1 ( UART_NB_BIT_8 | UART_PARITY_EVEN | UART_NB_STOP_BIT_1 )
#define UART_5E2 ( UART_NB_BIT_5 | UART_PARITY_EVEN | UART_NB_STOP_BIT_2 )
#define UART_6E2 ( UART_NB_BIT_6 | UART_PARITY_EVEN | UART_NB_STOP_BIT_2 )
#define UART_7E2 ( UART_NB_BIT_7 | UART_PARITY_EVEN | UART_NB_STOP_BIT_2 )
#define UART_8E2 ( UART_NB_BIT_8 | UART_PARITY_EVEN | UART_NB_STOP_BIT_2 )
#define UART_5O1 ( UART_NB_BIT_5 | UART_PARITY_ODD  | UART_NB_STOP_BIT_1 )
#define UART_6O1 ( UART_NB_BIT_6 | UART_PARITY_ODD  | UART_NB_STOP_BIT_1 )
#define UART_7O1 ( UART_NB_BIT_7 | UART_PARITY_ODD  | UART_NB_STOP_BIT_1 )
#define UART_8O1 ( UART_NB_BIT_8 | UART_PARITY_ODD  | UART_NB_STOP_BIT_1 )
#define UART_5O2 ( UART_NB_BIT_5 | UART_PARITY_ODD  | UART_NB_STOP_BIT_2 )
#define UART_6O2 ( UART_NB_BIT_6 | UART_PARITY_ODD  | UART_NB_STOP_BIT_2 )
#define UART_7O2 ( UART_NB_BIT_7 | UART_PARITY_ODD  | UART_NB_STOP_BIT_2 )
#define UART_8O2 ( UART_NB_BIT_8 | UART_PARITY_ODD  | UART_NB_STOP_BIT_2 )

/*
#define UART_5N1 0x10
#define UART_6N1 0x14
#define UART_7N1 0x18
#define UART_8N1 0x1c
#define UART_5N2 0x30
#define UART_6N2 0x34
#define UART_7N2 0x38
#define UART_8N2 0x3c
#define UART_5E1 0x12
#define UART_6E1 0x16
#define UART_7E1 0x1a
#define UART_8E1 0x1e
#define UART_5E2 0x32
#define UART_6E2 0x36
#define UART_7E2 0x3a
#define UART_8E2 0x3e
#define UART_5O1 0x13
#define UART_6O1 0x17
#define UART_7O1 0x1b
#define UART_8O1 0x1f
#define UART_5O2 0x33
#define UART_6O2 0x37
#define UART_7O2 0x3b
#define UART_8O2 0x3f
*/

// Options for `mode` argument of uart_init
#define UART_FULL     0
#define UART_RX_ONLY  1
#define UART_TX_ONLY  2

#define UART_TX_FIFO_SIZE 0x80

struct uart_struct_t;
typedef struct uart_struct_t uart_t;


uart_t* uartBegin(uint8_t uart_nr, uint32_t baudrate, uint32_t config, int8_t rxPin, int8_t txPin, uint16_t queueLen, bool inverted);
void uartEnd(uart_t* uart, uint8_t rxPin, uint8_t txPin);

uint32_t uartAvailable(uart_t* uart);
uint32_t uartAvailableForWrite(uart_t* uart);
uint8_t uartRead(uart_t* uart);
uint8_t uartPeek(uart_t* uart);

void uartWrite(uart_t* uart, uint8_t c);
void uartWriteBuf(uart_t* uart, const uint8_t * data, size_t len);

void uartFlush(uart_t* uart);
void uartFlushTxOnly(uart_t* uart, bool txOnly );

void uartSetBaudRate(uart_t* uart, uint32_t baud_rate);
uint32_t uartGetBaudRate(uart_t* uart);

size_t uartResizeRxBuffer(uart_t* uart, size_t new_size);

void uartSetRxInvert(uart_t* uart, bool invert);

void uartSetDebug(uart_t* uart);
int uartGetDebug();

void uartStartDetectBaudrate(uart_t *uart);
unsigned long uartDetectBaudrate(uart_t *uart);

bool uartRxActive(uart_t* uart);

#ifdef __cplusplus
}
#endif

#endif /* MAIN_ESP32_HAL_UART_H_ */
