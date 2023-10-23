/* Definiciones de secciones de memoria */

MEMORY
{
  dport0_0_seg : org = 0x3ff00000, len = 0x10
  dram0_0_seg : org = 0x3ffe8000, len = 0x14000
  iram1_0_seg : org = 0x40100000, len = 0x8000
}

/* Definiciones de secciones de enlace */

SECTIONS
{
  .text : ALIGN(4)
  {
    *(.text .text.* .irom0.text .irom.text)
  } >dram0_0_seg

  .rodata : ALIGN(4)
  {
    *(.rodata .rodata.* .irom0.rodata .irom.rodata)
  } >dram0_0_seg

  .bss : ALIGN(4)
  {
    _bss_start = .;
    *(.bss .bss.*)
    *(COMMON)
    _bss_end = .;
  } >dram0_0_seg

  .data : ALIGN(4)
  {
    _data_start = .;
    *(.data .data.*)
    _data_end = .;
  } >dram0_0_seg

  .dport0_0 : ALIGN(4)
  {
    *(.dport0_0)
  } >dport0_0_seg

  .iram0.text : ALIGN(4)
  {
    *(.iram0.text)
    *(.iram0.text.*)
    *(.iram.text)
    *(.iram.text.*)
  } >iram1_0_seg AT >dram0_0_seg

  .iram0.rodata : ALIGN(4)
  {
    *(.iram0.rodata)
    *(.iram0.rodata.*)
    *(.iram.rodata)
    *(.iram.rodata.*)
  } >iram1_0_seg AT >dram0_0_seg

  .iram0.bss : ALIGN(4)
  {
    _iram_bss_start = .;
    *(.iram0.bss)
    *(.iram0.bss.*)
    *(.iram.bss)
    *(.iram.bss.*)
    _iram_bss_end = .;
  } >iram1_0_seg
}

