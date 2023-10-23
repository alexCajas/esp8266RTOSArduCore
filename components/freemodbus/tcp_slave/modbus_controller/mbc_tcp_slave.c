/* Copyright 2018 Espressif Systems (Shanghai) PTE LTD
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
*/

// mbc_tcp_slave.c
// Implementation of the Modbus controller TCP slave

#include <sys/time.h>               // for calculation of time stamp in milliseconds
#include "esp_log.h"                // for log_write
#include "mb.h"                     // for mb types definition
#include "mbutils.h"                // for mbutils functions definition for stack callback
#include "port.h"                   // for port callback functions and defines
#include "sdkconfig.h"              // for KConfig values
#include "esp_modbus_common.h"      // for common defines
#include "esp_modbus_slave.h"       // for public slave interface types
#include "mbc_slave.h"              // for private slave interface types
#include "mbc_tcp_slave.h"          // for tcp slave mb controller defines
#include "port_tcp_slave.h"         // for tcp slave port defines
#include "esp_timer.h"
// Shared pointer to interface structure
static mb_slave_interface_t* mbs_interface_ptr = NULL;

// The helper function to get time stamp in microseconds
static uint64_t get_time_stamp(void)
{
    uint64_t time_stamp = esp_timer_get_time();
    return time_stamp;
}

// Modbus task function
static void modbus_tcp_slave_task(void *pvParameters)
{
    MB_SLAVE_ASSERT(mbs_interface_ptr != NULL);
    mb_slave_options_t* mbs_opts = &mbs_interface_ptr->opts;

    // Main Modbus stack processing cycle
    for (;;) {
        BaseType_t status = xEventGroupWaitBits(mbs_opts->mbs_event_group,
                                                (BaseType_t)(MB_EVENT_STACK_STARTED),
                                                pdFALSE, // do not clear bits
                                                pdFALSE,
                                                portMAX_DELAY);
        // Check if stack started then poll for data
        if (status & MB_EVENT_STACK_STARTED) {
            (void)eMBPoll(); // allow stack to process data
        }
    }
}

// Setup Modbus controller parameters
static esp_err_t mbc_tcp_slave_setup(void* comm_info)
{
    MB_SLAVE_ASSERT(mbs_interface_ptr != NULL);
    mb_slave_options_t* mbs_opts = &mbs_interface_ptr->opts;
    MB_SLAVE_CHECK((comm_info != NULL), ESP_ERR_INVALID_ARG,
                    "mb wrong communication settings.");
    mb_communication_info_t* comm_settings = (mb_communication_info_t*)comm_info;
    MB_SLAVE_CHECK((comm_settings->ip_mode == MB_MODE_TCP),
                ESP_ERR_INVALID_ARG, "mb incorrect mode = (0x%x).", (uint8_t)comm_settings->ip_mode);
    MB_SLAVE_CHECK(((comm_settings->ip_addr_type == MB_IPV4) || (comm_settings->ip_addr_type == MB_IPV6)),
                    ESP_ERR_INVALID_ARG, "mb incorrect addr type = (0x%x).", (uint8_t)comm_settings->ip_addr_type);
    MB_SLAVE_CHECK((comm_settings->ip_netif_ptr != NULL),
                        ESP_ERR_INVALID_ARG, "mb incorrect iface address.");
    // Set communication options of the controller
    mbs_opts->mbs_comm = *comm_settings;
    return ESP_OK;
}

// Start Modbus controller start function
static esp_err_t mbc_tcp_slave_start(void)
{
    MB_SLAVE_ASSERT(mbs_interface_ptr != NULL);
    mb_slave_options_t* mbs_opts = &mbs_interface_ptr->opts;
    eMBErrorCode status = MB_EIO;

    // Initialize Modbus stack using mbcontroller parameters
    status = eMBTCPInit((USHORT)mbs_opts->mbs_comm.ip_port);
    MB_SLAVE_CHECK((status == MB_ENOERR), ESP_ERR_INVALID_STATE,
            "mb stack initialization failure, eMBInit() returns (0x%x).", status);

    eMBPortProto proto = (mbs_opts->mbs_comm.ip_mode == MB_MODE_TCP) ? MB_PROTO_TCP : MB_PROTO_UDP;
    eMBPortIpVer ip_ver = (mbs_opts->mbs_comm.ip_addr_type == MB_IPV4) ? MB_PORT_IPV4 : MB_PORT_IPV6;
    vMBTCPPortSlaveSetNetOpt(mbs_opts->mbs_comm.ip_netif_ptr, ip_ver, proto, (char*)mbs_opts->mbs_comm.ip_addr);
    vMBTCPPortSlaveStartServerTask();

    status = eMBEnable();
    MB_SLAVE_CHECK((status == MB_ENOERR), ESP_ERR_INVALID_STATE,
            "mb TCP stack start failure, eMBEnable() returned (0x%x).", (uint32_t)status);
    // Set the mbcontroller start flag
    EventBits_t flag = xEventGroupSetBits(mbs_opts->mbs_event_group,
                                            (EventBits_t)MB_EVENT_STACK_STARTED);
    MB_SLAVE_CHECK((flag & MB_EVENT_STACK_STARTED),
                ESP_ERR_INVALID_STATE, "mb stack start event set error.");
    return ESP_OK;
}

// Modbus controller destroy function
static esp_err_t mbc_tcp_slave_destroy(void)
{
    MB_SLAVE_ASSERT(mbs_interface_ptr != NULL);
    mb_slave_options_t* mbs_opts = &mbs_interface_ptr->opts;
    eMBErrorCode mb_error = MB_ENOERR;
    // Stop polling by clearing correspondent bit in the event group
    EventBits_t flag = xEventGroupClearBits(mbs_opts->mbs_event_group,
                                    (EventBits_t)MB_EVENT_STACK_STARTED);
    MB_SLAVE_CHECK((flag & MB_EVENT_STACK_STARTED),
                ESP_ERR_INVALID_STATE, "mb stack stop event failure.");
    // Disable and then destroy the Modbus stack
    mb_error = eMBDisable();
    MB_SLAVE_CHECK((mb_error == MB_ENOERR), ESP_ERR_INVALID_STATE, "mb stack disable failure.");
    (void)vTaskDelete(mbs_opts->mbs_task_handle);
    (void)vQueueDelete(mbs_opts->mbs_notification_queue_handle);
    (void)vEventGroupDelete(mbs_opts->mbs_event_group);
    (void)vMBTCPPortClose();
    free(mbs_interface_ptr);
    vMBPortSetMode((UCHAR)MB_PORT_INACTIVE);
    mbs_interface_ptr = NULL;
    return ESP_OK;
}

esp_err_t mbc_tcp_slave_set_descriptor(const mb_register_area_descriptor_t descr_info)
{
    MB_SLAVE_ASSERT(mbs_interface_ptr != NULL);
    mb_slave_options_t* mbs_opts = &mbs_interface_ptr->opts;
    MB_SLAVE_CHECK(((descr_info.type < MB_PARAM_COUNT) && (descr_info.type >= MB_PARAM_HOLDING)),
                ESP_ERR_INVALID_ARG, "mb incorrect modbus instance type = (0x%x).",
                (uint32_t)descr_info.type);
    MB_SLAVE_CHECK((descr_info.address != NULL),
                ESP_ERR_INVALID_ARG, "mb instance pointer is NULL.");
    MB_SLAVE_CHECK((descr_info.size >= MB_INST_MIN_SIZE) && (descr_info.size < (MB_INST_MAX_SIZE)),
                ESP_ERR_INVALID_ARG, "mb instance size is incorrect = (0x%x).",
                (uint32_t)descr_info.size);
    mbs_opts->mbs_area_descriptors[descr_info.type] = descr_info;
    return ESP_OK;
}

// Helper function to send parameter information to application task
static esp_err_t send_param_info(mb_event_group_t par_type, uint16_t mb_offset,
                                    uint8_t* par_address, uint16_t par_size)
{
    MB_SLAVE_ASSERT(mbs_interface_ptr != NULL);
    mb_slave_options_t* mbs_opts = &mbs_interface_ptr->opts;
    esp_err_t error = ESP_FAIL;
    mb_param_info_t par_info;
    // Check if queue is not full the send parameter information
    par_info.type = par_type;
    par_info.size = par_size;
    par_info.address = par_address;
    par_info.time_stamp = get_time_stamp();
    par_info.mb_offset = mb_offset;
    BaseType_t status = xQueueSend(mbs_opts->mbs_notification_queue_handle,
                                    &par_info, MB_PAR_INFO_TOUT);
    if (pdTRUE == status) {
        ESP_LOGD(MB_SLAVE_TAG, "Queue send parameter info (type, address, size): %d, 0x%.4x, %d",
                par_type, (uint32_t)par_address, par_size);
        error = ESP_OK;
    } else if (errQUEUE_FULL == status) {
        ESP_LOGD(MB_SLAVE_TAG, "Parameter queue is overflowed.");
    }
    return error;
}

// Helper function to send notification
static esp_err_t send_param_access_notification(mb_event_group_t event)
{
    MB_SLAVE_ASSERT(mbs_interface_ptr != NULL);
    mb_slave_options_t* mbs_opts = &mbs_interface_ptr->opts;
    esp_err_t err = ESP_FAIL;
    mb_event_group_t bits = (mb_event_group_t)xEventGroupSetBits(mbs_opts->mbs_event_group,
                                                                    (EventBits_t)event);
    if (bits & event) {
        ESP_LOGD(MB_SLAVE_TAG, "The MB_REG_CHANGE_EVENT = 0x%.2x is set.", (uint8_t)event);
        err = ESP_OK;
    }
    return err;
}

// Blocking function to get event on parameter group change for application task
static mb_event_group_t mbc_tcp_slave_check_event(mb_event_group_t group)
{
    MB_SLAVE_ASSERT(mbs_interface_ptr != NULL);
    mb_slave_options_t* mbs_opts = &mbs_interface_ptr->opts;
    MB_SLAVE_ASSERT(mbs_opts->mbs_event_group != NULL);
    BaseType_t status = xEventGroupWaitBits(mbs_opts->mbs_event_group, (BaseType_t)group,
                                            pdTRUE , pdFALSE, portMAX_DELAY);
    return (mb_event_group_t)status;
}

// Function to get notification about parameter change from application task
static esp_err_t mbc_tcp_slave_get_param_info(mb_param_info_t* reg_info, uint32_t timeout)
{
    MB_SLAVE_ASSERT(mbs_interface_ptr != NULL);
    mb_slave_options_t* mbs_opts = &mbs_interface_ptr->opts;
    esp_err_t err = ESP_ERR_TIMEOUT;
    MB_SLAVE_CHECK((mbs_opts->mbs_notification_queue_handle != NULL),
                ESP_ERR_INVALID_ARG, "mb queue handle is invalid.");
    MB_SLAVE_CHECK((reg_info != NULL), ESP_ERR_INVALID_ARG, "mb register information is invalid.");
    BaseType_t status = xQueueReceive(mbs_opts->mbs_notification_queue_handle,
                                        reg_info, pdMS_TO_TICKS(timeout));
    if (status == pdTRUE) {
        err = ESP_OK;
    }
    return err;
}

/* ----------------------- Callback functions for Modbus stack ---------------------------------*/
// These are executed by modbus stack to read appropriate type of registers.

// This is required to suppress warning when register start address is zero
#pragma GCC diagnostic ignored "-Wtype-limits"

// Callback function for reading of MB Input Registers
eMBErrorCode eMBRegInputCBTcpSlave(UCHAR * pucRegBuffer, USHORT usAddress,
                                USHORT usNRegs)
{
    MB_SLAVE_ASSERT(mbs_interface_ptr != NULL);
    mb_slave_options_t* mbs_opts = &mbs_interface_ptr->opts;
    MB_SLAVE_ASSERT(pucRegBuffer != NULL);
    USHORT usRegInputNregs = (USHORT)(mbs_opts->mbs_area_descriptors[MB_PARAM_INPUT].size >> 1); // Number of input registers
    USHORT usInputRegStart = (USHORT)mbs_opts->mbs_area_descriptors[MB_PARAM_INPUT].start_offset; // Get Modbus start address
    UCHAR* pucInputBuffer = (UCHAR*)mbs_opts->mbs_area_descriptors[MB_PARAM_INPUT].address; // Get instance address
    USHORT usRegs = usNRegs;
    eMBErrorCode eStatus = MB_ENOERR;
    USHORT iRegIndex;
    // If input or configuration parameters are incorrect then return an error to stack layer
    if ((usAddress >= usInputRegStart)
            && (pucInputBuffer != NULL)
            && (usNRegs >= 1)
            && ((usAddress + usRegs) <= (usInputRegStart + usRegInputNregs + 1))
            && (usRegInputNregs >= 1)) {
        iRegIndex = (USHORT)(usAddress - usInputRegStart - 1);
        iRegIndex <<= 1; // register Address to byte address
        pucInputBuffer += iRegIndex;
        UCHAR* pucBufferStart = pucInputBuffer;
        while (usRegs > 0) {
            _XFER_2_RD(pucRegBuffer, pucInputBuffer);
            iRegIndex += 2;
            usRegs -= 1;
        }
        // Send access notification
        (void)send_param_access_notification(MB_EVENT_INPUT_REG_RD);
        // Send parameter info to application task
        (void)send_param_info(MB_EVENT_INPUT_REG_RD, (uint16_t)usAddress,
                        (uint8_t*)pucBufferStart, (uint16_t)usNRegs);
    } else {
        eStatus = MB_ENOREG;
    }
    return eStatus;
}

// Callback function for reading of MB Holding Registers
// Executed by stack when request to read/write holding registers is received
eMBErrorCode eMBRegHoldingCBTcpSlave(UCHAR * pucRegBuffer, USHORT usAddress,
        USHORT usNRegs, eMBRegisterMode eMode)
{
    MB_SLAVE_ASSERT(mbs_interface_ptr != NULL);
    mb_slave_options_t* mbs_opts = &mbs_interface_ptr->opts;
    MB_SLAVE_ASSERT(pucRegBuffer != NULL);
    USHORT usRegHoldingNregs = (USHORT)(mbs_opts->mbs_area_descriptors[MB_PARAM_HOLDING].size >> 1);
    USHORT usRegHoldingStart = (USHORT)mbs_opts->mbs_area_descriptors[MB_PARAM_HOLDING].start_offset;
    UCHAR* pucHoldingBuffer = (UCHAR*)mbs_opts->mbs_area_descriptors[MB_PARAM_HOLDING].address;
    eMBErrorCode eStatus = MB_ENOERR;
    USHORT iRegIndex;
    USHORT usRegs = usNRegs;
    // Check input and configuration parameters for correctness
    if ((usAddress >= usRegHoldingStart)
            && (pucHoldingBuffer != NULL)
            && ((usAddress + usRegs) <= (usRegHoldingStart + usRegHoldingNregs + 1))
            && (usRegHoldingNregs >= 1)
            && (usNRegs >= 1)) {
        iRegIndex = (USHORT) (usAddress - usRegHoldingStart - 1);
        iRegIndex <<= 1; // register Address to byte address
        pucHoldingBuffer += iRegIndex;
        UCHAR* pucBufferStart = pucHoldingBuffer;
        switch (eMode) {
            case MB_REG_READ:
                while (usRegs > 0) {
                    _XFER_2_RD(pucRegBuffer, pucHoldingBuffer);
                    iRegIndex += 2;
                    usRegs -= 1;
                };
                // Send access notification
                (void)send_param_access_notification(MB_EVENT_HOLDING_REG_RD);
                // Send parameter info
                (void)send_param_info(MB_EVENT_HOLDING_REG_RD, (uint16_t)usAddress,
                                (uint8_t*)pucBufferStart, (uint16_t)usNRegs);
                break;
            case MB_REG_WRITE:
                while (usRegs > 0) {
                    _XFER_2_WR(pucHoldingBuffer, pucRegBuffer);
                    pucHoldingBuffer += 2;
                    iRegIndex += 2;
                    usRegs -= 1;
                };
                // Send access notification
                (void)send_param_access_notification(MB_EVENT_HOLDING_REG_WR);
                // Send parameter info
                (void)send_param_info(MB_EVENT_HOLDING_REG_WR, (uint16_t)usAddress,
                                (uint8_t*)pucBufferStart, (uint16_t)usNRegs);
                break;
        }
    } else {
        eStatus = MB_ENOREG;
    }
    return eStatus;
}

// Callback function for reading of MB Coils Registers
eMBErrorCode eMBRegCoilsCBTcpSlave(UCHAR* pucRegBuffer, USHORT usAddress,
        USHORT usNCoils, eMBRegisterMode eMode)
{
    MB_SLAVE_ASSERT(mbs_interface_ptr != NULL);
    mb_slave_options_t* mbs_opts = &mbs_interface_ptr->opts;
    MB_SLAVE_ASSERT(NULL != pucRegBuffer);
    USHORT usRegCoilNregs = (USHORT)(mbs_opts->mbs_area_descriptors[MB_PARAM_COIL].size >> 1); // number of registers in storage area
    USHORT usRegCoilsStart = (USHORT)mbs_opts->mbs_area_descriptors[MB_PARAM_COIL].start_offset; // MB offset of coils registers
    UCHAR* pucRegCoilsBuf = (UCHAR*)mbs_opts->mbs_area_descriptors[MB_PARAM_COIL].address;
    eMBErrorCode eStatus = MB_ENOERR;
    USHORT iRegIndex;
    USHORT usCoils = usNCoils;
    usAddress--; // The address is already +1
    if ((usAddress >= usRegCoilsStart)
            && (usRegCoilNregs >= 1)
            && ((usAddress + usCoils) <= (usRegCoilsStart + (usRegCoilNregs << 4) + 1))
            && (pucRegCoilsBuf != NULL)
            && (usNCoils >= 1)) {
        iRegIndex = (USHORT) (usAddress - usRegCoilsStart);
        CHAR* pucCoilsDataBuf = (CHAR*)(pucRegCoilsBuf + (iRegIndex >> 3));
        switch (eMode) {
            case MB_REG_READ:
                while (usCoils > 0) {
                    UCHAR ucResult = xMBUtilGetBits((UCHAR*)pucRegCoilsBuf, iRegIndex, 1);
                    xMBUtilSetBits(pucRegBuffer, iRegIndex - (usAddress - usRegCoilsStart), 1, ucResult);
                    iRegIndex++;
                    usCoils--;
                }
                // Send an event to notify application task about event
                (void)send_param_access_notification(MB_EVENT_COILS_RD);
                (void)send_param_info(MB_EVENT_COILS_RD, (uint16_t)usAddress,
                                (uint8_t*)(pucCoilsDataBuf), (uint16_t)usNCoils);
                break;
            case MB_REG_WRITE:
                while (usCoils > 0) {
                    UCHAR ucResult = xMBUtilGetBits(pucRegBuffer,
                            iRegIndex - (usAddress - usRegCoilsStart), 1);
                    xMBUtilSetBits((uint8_t*)pucRegCoilsBuf, iRegIndex, 1, ucResult);
                    iRegIndex++;
                    usCoils--;
                }
                // Send an event to notify application task about event
                (void)send_param_access_notification(MB_EVENT_COILS_WR);
                (void)send_param_info(MB_EVENT_COILS_WR, (uint16_t)usAddress,
                                (uint8_t*)pucCoilsDataBuf, (uint16_t)usNCoils);
                break;
        } // switch ( eMode )
    } else {
        // If the configuration or input parameters are incorrect then return error to stack
        eStatus = MB_ENOREG;
    }
    return eStatus;
}

// Callback function for reading of MB Discrete Input Registers
eMBErrorCode eMBRegDiscreteCBTcpSlave(UCHAR* pucRegBuffer, USHORT usAddress,
                            USHORT usNDiscrete)
{
    MB_SLAVE_ASSERT(mbs_interface_ptr != NULL);
    mb_slave_options_t* mbs_opts = &mbs_interface_ptr->opts;
    MB_SLAVE_ASSERT(pucRegBuffer != NULL);
    USHORT usRegDiscreteNregs = (USHORT)(mbs_opts->mbs_area_descriptors[MB_PARAM_DISCRETE].size >> 1); // number of registers in storage area
    USHORT usRegDiscreteStart = (USHORT)mbs_opts->mbs_area_descriptors[MB_PARAM_DISCRETE].start_offset; // MB offset of registers
    UCHAR* pucRegDiscreteBuf = (UCHAR*)mbs_opts->mbs_area_descriptors[MB_PARAM_DISCRETE].address; // the storage address
    eMBErrorCode eStatus = MB_ENOERR;
    USHORT iRegIndex, iRegBitIndex, iNReg;
    UCHAR* pucDiscreteInputBuf;
    iNReg = usNDiscrete / 8 + 1;
    pucDiscreteInputBuf = (UCHAR*) pucRegDiscreteBuf;
    // It already plus one in modbus function method.
    usAddress--;
    if ((usAddress >= usRegDiscreteStart)
            && (usRegDiscreteNregs >= 1)
            && (pucRegDiscreteBuf != NULL)
            && ((usAddress + usNDiscrete) <= (usRegDiscreteStart + (usRegDiscreteNregs * 16)))
            && (usNDiscrete >= 1)) {
        iRegIndex = (USHORT) (usAddress - usRegDiscreteStart) / 8; // Get register index in the buffer for bit number
        iRegBitIndex = (USHORT)(usAddress - usRegDiscreteStart) % 8; // Get bit index
        UCHAR* pucTempBuf = &pucDiscreteInputBuf[iRegIndex];
        while (iNReg > 0) {
            *pucRegBuffer++ = xMBUtilGetBits(&pucDiscreteInputBuf[iRegIndex++], iRegBitIndex, 8);
            iNReg--;
        }
        pucRegBuffer--;
        // Last discrete
        usNDiscrete = usNDiscrete % 8;
        // Filling zero to high bit
        *pucRegBuffer = *pucRegBuffer << (8 - usNDiscrete);
        *pucRegBuffer = *pucRegBuffer >> (8 - usNDiscrete);
        // Send an event to notify application task about event
        (void)send_param_access_notification(MB_EVENT_DISCRETE_RD);
        (void)send_param_info(MB_EVENT_DISCRETE_RD, (uint16_t)usAddress,
                            (uint8_t*)pucTempBuf, (uint16_t)usNDiscrete);
    } else {
        eStatus = MB_ENOREG;
    }
    return eStatus;
}
#pragma GCC diagnostic pop   // require GCC

// Initialization of Modbus controller
esp_err_t mbc_tcp_slave_create(void** handler)
{
    // Allocate space for options
    if (mbs_interface_ptr == NULL) {
        mbs_interface_ptr = malloc(sizeof(mb_slave_interface_t));
    }
    MB_SLAVE_ASSERT(mbs_interface_ptr != NULL);
    mb_slave_options_t* mbs_opts = &mbs_interface_ptr->opts;
    mbs_opts->port_type = MB_PORT_TCP_SLAVE; // set interface port type

    vMBPortSetMode((UCHAR)MB_PORT_TCP_SLAVE);

    // Set default values of communication options
    mbs_opts->mbs_comm.ip_port = MB_TCP_DEFAULT_PORT;

    // Initialization of active context of the Modbus controller
    BaseType_t status = 0;

    // Parameter change notification queue
    mbs_opts->mbs_event_group = xEventGroupCreate();
    MB_SLAVE_CHECK((mbs_opts->mbs_event_group != NULL),
            ESP_ERR_NO_MEM, "mb event group error.");
    // Parameter change notification queue
    mbs_opts->mbs_notification_queue_handle = xQueueCreate(
                                                MB_CONTROLLER_NOTIFY_QUEUE_SIZE,
                                                sizeof(mb_param_info_t));
    MB_SLAVE_CHECK((mbs_opts->mbs_notification_queue_handle != NULL),
            ESP_ERR_NO_MEM, "mb notify queue creation error.");
    // Create Modbus controller task
    status = xTaskCreate((void*)&modbus_tcp_slave_task,
                            "modbus_tcp_slave_task",
                            MB_CONTROLLER_STACK_SIZE,
                            NULL,
                            MB_CONTROLLER_PRIORITY,
                            &mbs_opts->mbs_task_handle);
    if (status != pdPASS) {
        vTaskDelete(mbs_opts->mbs_task_handle);
        MB_SLAVE_CHECK((status == pdPASS), ESP_ERR_NO_MEM,
                "mb controller task creation error, xTaskCreate() returns (0x%x).",
                (uint32_t)status);
    }

    // The task is created but handle is incorrect
    MB_SLAVE_ASSERT(mbs_opts->mbs_task_handle != NULL);

    // Initialization of interface pointers
    mbs_interface_ptr->init = mbc_tcp_slave_create;
    mbs_interface_ptr->destroy = mbc_tcp_slave_destroy;
    mbs_interface_ptr->setup = mbc_tcp_slave_setup;
    mbs_interface_ptr->start = mbc_tcp_slave_start;
    mbs_interface_ptr->check_event = mbc_tcp_slave_check_event;
    mbs_interface_ptr->get_param_info = mbc_tcp_slave_get_param_info;
    mbs_interface_ptr->set_descriptor = mbc_tcp_slave_set_descriptor;

    // Initialize stack callback function pointers
    mbs_interface_ptr->slave_reg_cb_discrete = eMBRegDiscreteCBTcpSlave;
    mbs_interface_ptr->slave_reg_cb_input = eMBRegInputCBTcpSlave;
    mbs_interface_ptr->slave_reg_cb_holding = eMBRegHoldingCBTcpSlave;
    mbs_interface_ptr->slave_reg_cb_coils = eMBRegCoilsCBTcpSlave;

    *handler = (void*)mbs_interface_ptr;

    return ESP_OK;
}
