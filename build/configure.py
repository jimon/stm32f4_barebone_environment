# toolchain configuration
arm_gcc				= "arm-none-eabi-gcc"
arm_as				= "arm-none-eabi-as"
arm_objcopy			= "arm-none-eabi-objcopy"
stm32cubef4_drivers	= "C:/work/stm32/STM32Cube_FW_F4_V1.4.0/Drivers"
stlink_cli			= "C:/Program Files (x86)/STMicroelectronics/STM32 ST-LINK Utility/ST-LINK Utility/ST-LINK_CLI.exe"
# -c SWD -p main.bin -Rst -Run

# flash configuration
flash_base			= "0x08000000"
flash_offset		= "0"
flash_signoffset	= "0"
hal					= "STM32F407xx"

# stm32cubef4 features configuration
features = {
	"Adafruit_Shield":						False,
	"ampire480272":							False,
	"ampire640480":							False,
	"Common":								False,
	"cs43l22":								False,
	"ili9325":								False,
	"ili9341":								False,
	"l3gd20":								False,
	"lis302dl":								False,
	"lis3dsh":								False,
	"lsm303dlhc":							False,
	"ov2640":								False,
	"st7735":								False,
	"stmpe1600":							False,
	"stmpe811":								False,
	"ts3510":								False,
	"wm8994":								False,
	"STM324x9I_EVAL":						False,
	"STM324xG_EVAL":						False,
	"STM32F4-Discovery":					True,
	"stm32f4_discovery_audio.c":			False,
	"stm32f4_discovery_accelerometer.c":	False,
	"STM32F401-Discovery":					False,
	"STM32F429I-Discovery":					False,
	"STM32F4xx-Nucleo":						False,
	"STM32F4xx/Source/Templates":			False,
	"CMSIS/Documentation":					False,
	"CMSIS/DSP_Lib":						False,
	"CMSIS/RTOS":							False,
	"CMSIS/Lib":							False,
}

def excluded(path):
	for name, val in features.items():
		if name in root and not val:
			return True
	return False

def any(files, with_ext):
	for file in files:
		if file.endswith(with_ext):
			return True
	return False

import os, glob
from pprint import pprint

include_dirs = ["."]
sources = {}

#for root, dir, files in os.walk("Drivers"):
#	enabled = True
#	for name, val in features.items():
#		if name in root and not val:
#			enabled = False
#			break
#
#	if not enabled:
#		continue
#
#
#	if any(files, ".h"):
#		include_dirs.append(root)
#
#	for file in files:
#		enabled = True
#		for name, val in features.items():
#			if name in file and not val:
#				enabled = False
#				break
#		if not enabled:
#			continue
#		if file.endswith(".c"):
#			sources_c.append(root + "/" + file)
#		if file.endswith(".cpp") or file.endswith(".cxx"):
#			sources_cpp.append(root + "/" + file)

import ninja_syntax

wr = ninja_syntax.Writer(open("build.ninja", "w"))
wr.comment("general settings")
wr.variable("flash_base", flash_base)
wr.variable("flash_offset", flash_offset)
wr.variable("flash_signoffset", flash_signoffset)
wr.variable("hal", hal)
wr.variable("defines", "-D $hal=1 -DVECT_TAB_OFFSET=$flash_offset+$flash_signoffset")

wr.comment("locations")
wr.variable("bin_cc", arm_gcc)
wr.variable("bin_as", arm_as)
wr.variable("bin_cp", arm_objcopy)
wr.variable("bin_stlink", stlink_cli)
wr.variable("include_paths", "".join(["-I" + f + " " for f in include_dirs]))
wr.variable("linkerscript", "STM32F407VG_FLASH.ld")

wr.comment("compiler flags")
wr.variable("cpuflags", "-mcpu=cortex-m4 -mthumb -mlittle-endian -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb-interwork")
wr.variable("optflags", "-O3 -fdata-sections -ffunction-sections -fsingle-precision-constant")
wr.variable("debugflags", "-g")
wr.variable("cflags", "$cpuflags $debugflags $optflags -std=c99 $defines $include_paths")
wr.variable("ldflags", "$cpuflags $debugflags -O3 -T$linkerscript -Wl,--gc-sections -lm")
wr.variable("asflags", "$cpuflags $debugflags")

wr.comment("rules")
wr.rule("ldscript", "python tool_strrepl.py $in $out FLASH_BASE $flash_base FLASH_OFFSET $flash_offset FLASH_SIGNOFFSET $flash_signoffset")
wr.rule("cc", "$bin_cc $cflags -o $out -c $in")
wr.rule("ld", "$bin_cc $ldflags -o $out $in")
wr.rule("as", "$bin_as $asflags -o $out -c $in")
wr.rule("cp", "$bin_cp -O binary $in $out")
wr.rule("sign", "python tool_sign.py $in $out $flash_signoffset")

wr.comment("build")

wr.comment("deploy")
#sources_c.extend(["main.c", "stm32f4xx_it.c", "system_stm32f4xx.c", "periph/clock.c"])
#objs = []
#for s in sources_c:
#	obj = os.path.basename(s) + ".o"
#	objs.append(obj)
#	wr.build(obj, "c", s)

#wr.build("startup_stm32f407xx.o", "a", "startup_stm32f407xx.s")
#objs.append("startup_stm32f407xx.s")

#wr.build("main.elf", "l", objs)
#wr.build("main.binns", "copy", "main.elf")
#wr.build("main.bin", "sign", "main.binns")
