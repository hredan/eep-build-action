REM Windows build script

set ARDUINO_PATH="C:\Program Files (x86)\Arduino"
set LOCALPATH=%~dp0
set BUILD_PATH=%LOCALPATH%..\build_esp8266
set BUILD_CACHE_PATH=%LOCALPATH%..\cache_esp8266
set HOME=%HOMEDRIVE%%HOMEPATH%

set GCC_VERSION=3.0.4-gcc10.3-1757bed

set BUILD_PARAMETER=-logger=machine -hardware %ARDUINO_PATH%\hardware^
 -hardware %HOME%\AppData\Local\Arduino15\packages^
 -tools %ARDUINO_PATH%\tools-builder^
 -tools %ARDUINO_PATH%\hardware\tools\avr^
 -tools %HOME%\AppData\Local\Arduino15\packages^
 -built-in-libraries %ARDUINO_PATH%\libraries^
 -libraries %HOME%\Documents\Arduino\libraries^
 -fqbn=esp8266:esp8266:d1_mini:xtal=160,vt=flash,exception=disabled,stacksmash=disabled^
,ssl=all,mmu=3232,non32xfer=fast,eesz=4M2M,ip=hb2f,dbg=Disabled,lvl=None____,wipe=none,baud=921600^
 -ide-version=10816 -build-path %BUILD_PATH% -warnings=none -build-cache %BUILD_CACHE_PATH% -prefs=build.warn_data_percentage=75^
 -prefs=runtime.tools.python3.path=%HOME%\AppData\Local\Arduino15\packages\esp8266\tools\python3\3.7.2-post1^
 -prefs=runtime.tools.python3-3.7.2-post1.path=%HOME%\AppData\Local\Arduino15\packages\esp8266\tools\python3\3.7.2-post1^
 -prefs=runtime.tools.mklittlefs.path=%HOME%\AppData\Local\Arduino15\packages\esp8266\tools\mklittlefs\%GCC_VERSION%^
 -prefs=runtime.tools.mklittlefs-%GCC_VERSION%.path=%HOME%\AppData\Local\Arduino15\packages\esp8266\tools\mklittlefs\%GCC_VERSION%^
 -prefs=runtime.tools.mkspiffs.path=%HOME%\AppData\Local\Arduino15\packages\esp8266\tools\mkspiffs\%GCC_VERSION%^
 -prefs=runtime.tools.mkspiffs-%GCC_VERSION%.path=%HOME%\AppData\Local\Arduino15\packages\esp8266\tools\mkspiffs\%GCC_VERSION%^
 -prefs=runtime.tools.xtensa-lx106-elf-gcc.path=%HOME%\AppData\Local\Arduino15\packages\esp8266\tools\xtensa-lx106-elf-gcc\%GCC_VERSION%^
 -prefs=runtime.tools.xtensa-lx106-elf-gcc-%GCC_VERSION%.path=%HOME%\AppData\Local\Arduino15\packages\esp8266\tools\xtensa-lx106-elf-gcc\%GCC_VERSION%^
 -verbose ..\ESP_jQuery_Mobile_Interface.ino

mkdir %BUILD_PATH%
mkdir %BUILD_CACHE_PATH%

set 

REM DUMP
%ARDUINO_PATH%\arduino-builder -dump-prefs %BUILD_PARAMETER%

REM COMPILE
%ARDUINO_PATH%\arduino-builder -compile %BUILD_PARAMETER%
pause