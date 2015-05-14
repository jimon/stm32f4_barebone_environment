# stm32f4 barebone environment

Ultra simple build environment for stm32f4 based projects

### Motivation

If you come from PC software development - stm32 build environments will look bulky, clumsy and awkward to you (for example arm keil). On other hand makefiles are so 90-x. So this small project tries to create the simplest possible environment based on more modern trends of building software.

This env is based on [https://github.com/carrotIndustries/stm32-template ](https://github.com/carrotIndustries/stm32-template ) but it doesn't require epm or openocd to build project.

### Prerequirements

- gcc arm embedded (download and unpack somewhere, will be easier if you add it to PATH)
- stm32cubef4 (download and unpack somewhere)
- st-link utility
- python
- ninja (for non windows env)

### Building

1. Set paths in build/configure.py
2. Run configure.bat or python build/configure.py
3. Run build\_and\_deploy.bat or ninja -C build_temp

### How it works

First we run configure script, it will walk through stm32cubef4 drivers and compile list of sources to build. Then it will generate ninja build file for us. [Ninja](https://martine.github.io/ninja/) is ultra simple and ultra fast build system with human readable make files. Then we run ninja and it will compile .bin file and run st-link to deploy it.
   