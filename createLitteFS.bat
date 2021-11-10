rem toolPath, "-c", dataPath, "-p", spiPage+"", "-b", spiBlock+"", "-s", (spiEnd - spiStart)+"", imagePath

set LOCALPATH=%~dp0
set BUILD_PATH=%LOCALPATH%..\build_data
set HOME=%HOMEDRIVE%%HOMEPATH%

mkdir %BUILD_PATH%
set TOOL_PATH=%HOME%\AppData\Local\Arduino15\packages\esp8266\tools\mklittlefs\3.0.4-gcc10.3-1757bed\mklittlefs.exe
%TOOL_PATH% -c ../data -p 256 -b 8192 -s 2072576 %BUILD_PATH%\littlefs.bin
pause