
features = {
	"Adafruit_Shield": False,
	"ampire480272": False,
	"ampire640480": False,
	"Common": False,
	"cs43l22": False,
	"ili9325": False,
	"ili9341": False,
	"l3gd20": False,
	"lis302dl": False,
	"lis3dsh": False,
	"lsm303dlhc": False,
	"ov2640": False,
	"st7735": False,
	"stmpe1600": False,
	"stmpe811": False,
	"ts3510": False,
	"wm8994": False,
	"STM324x9I_EVAL": False,
	"STM324xG_EVAL": False,
	"STM32F4-Discovery": True,
	
	"stm32f4_discovery_audio.c": False,
	"stm32f4_discovery_accelerometer.c": False,
	
	"STM32F401-Discovery": False,
	"STM32F429I-Discovery": False,
	"STM32F4xx-Nucleo": False,
	"STM32F4xx/Source/Templates": False,
	"CMSIS/Documentation": False,
	"CMSIS/DSP_Lib": False,
	"CMSIS/RTOS": False,
	"CMSIS/Lib": False,
}

def any(files, ext):
	for file in files:
		if file.endswith(ext):
			return True
	return False

import os, glob
from pprint import pprint

dirs = []
include_dirs = ["."]
sources_c = []
sources_cpp = []

for root, dir, files in os.walk("Drivers"):
	enabled = True
	for name, val in features.items():
		if name in root and not val:
			enabled = False
			break

	if not enabled:
		continue

	dirs.append(root)

	if any(files, ".h"):
		include_dirs.append(root)

	for file in files:
		enabled = True
		for name, val in features.items():
			if name in file and not val:
				enabled = False
				break
		if not enabled:
			continue
		if file.endswith(".c"):
			sources_c.append(root + "/" + file)
		if file.endswith(".cpp") or file.endswith(".cxx"):
			sources_cpp.append(root + "/" + file)

import ninja_syntax

wr = ninja_syntax.Writer(open("build.ninja", "w"))


wr.comment("settings")
wr.variable("paths", "".join(["-I" + f + " " for f in include_dirs]))
wr.variable("FLASH_BASE", "0x08000000")
wr.variable("FLASH_OFFSET", "0")
wr.variable("FLASH_SIGNOFFSET", "0")
wr.variable("defines", "-D STM32F407xx=1 -DVECT_TAB_OFFSET=$FLASH_OFFSET+$FLASH_SIGNOFFSET")

#MCU     = cortex-m4
#MCFLAGS =-mcpu=$(MCU) -mthumb -mlittle-endian -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb-interwork
#OPTIMIZE=-O3 -fdata-sections -ffunction-sections -fsingle-precision-constant
#DEBUG   =-g3
#CFLAGS  =$(MCFLAGS) $(DEBUG)  $(OPTIMIZE) -MP -MMD

wr.rule("ld_process", "sed s/FLASH_BASE/$FLASH_BASE/g;s/FLASH_OFFSET/$FLASH_OFFSET/g;s/FLASH_SIGNOFFSET/$FLASH_SIGNOFFSET/g < $in > $out")

#FLASH_BASE=0x08000000
#FLASH_OFFSET=0
#FLASH_SIGNOFFSET=0
#FLASH_PGM=$(shell printf 0x%x $$(($(FLASH_BASE)+$(FLASH_OFFSET))))


#wr.build("STM32F407VG_FLASH.ld", "ld_process", "STM32F407VG_FLASH.ld.in")

wr.variable("cc", "arm-none-eabi-gcc")
wr.variable("as", "arm-none-eabi-as")
wr.variable("cp", "arm-none-eabi-objcopy")

wr.variable("cpuflags", "-mcpu=cortex-m4 -mthumb -mlittle-endian -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb-interwork")
wr.variable("optflags", "-O3 -fdata-sections -ffunction-sections -fsingle-precision-constant")
wr.variable("cflags", "$cpuflags -g $optflags -std=c99 $defines $paths")
wr.variable("ldflags", "$cpuflags -g -O3 -TSTM32F407VG_FLASH.ld -Wl,--gc-sections -lm")
wr.variable("asflags", "$cpuflags -g")

wr.rule("c", "$cc $cflags -o $out -c $in")
wr.rule("l", "$cc $ldflags -o $out $in")
wr.rule("a", "$as $asflags -o $out -c $in")
wr.rule("copy", "$cp -O binary $in $out")
wr.rule("sign", "python sign.py $in $out $FLASH_SIGNOFFSET")

sources_c.extend(["main.c", "stm32f4xx_it.c", "system_stm32f4xx.c", "periph/clock.c"])
objs = []
for s in sources_c:
	obj = os.path.basename(s) + ".o"
	objs.append(obj)
	wr.build(obj, "c", s)

wr.build("startup_stm32f407xx.o", "a", "startup_stm32f407xx.s")
objs.append("startup_stm32f407xx.s")

#objs.append("STM32F407VG_FLASH.ld")

wr.build("main.elf", "l", objs)
wr.build("main.binns", "copy", "main.elf")
wr.build("main.bin", "sign", "main.binns")
