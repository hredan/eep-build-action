set TOOL=D:\StandAlone\arduino-cli_0.19.3_Windows_64bit\arduino-cli.exe

set LOCALPATH=%~dp0
set BUILD_PATH=%LOCALPATH%..\build_esp8266
set BUILD_CACHE_PATH=%LOCALPATH%..\cache_esp8266

mkdir %BUILD_PATH%
mkdir %BUILD_CACHE_PATH%

%TOOL% compile --fqbn esp8266:esp8266:d1_mini:xtal=160,vt=flash,exception=disabled,stacksmash=disabled,ssl=all,mmu=3232,non32xfer=fast,eesz=4M2M,ip=hb2f,dbg=Disabled,lvl=None____,wipe=none,baud=921600^
 --build-path %BUILD_PATH% --build-cache-path %BUILD_CACHE_PATH%^
 ..\ESP_jQuery_Mobile_Interface.ino -v
pause