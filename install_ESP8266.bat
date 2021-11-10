@echo off

REM find COM PORT
set COM_PORT=""
set DATA_FILE= "..\build_data\littlefs.bin"
set BIN_FILE="..\build_esp8266\ESP_jQuery_Mobile_Interface.ino.bin"

for /F "delims=" %%a in ('python -m serial.tools.list_ports serial ^| findstr /C:COM') do set COM_PORT=%%a

IF %COM_PORT% == "" GOTO ERROR_PORT
echo PORT: %COM_PORT%

IF NOT EXIST %DATA_FILE% (
	GOTO ERROR_DATA
)

IF NOT EXIST %BIN_FILE% (
	GOTO ERROR_BIN
)

python -m esptool --port %COM_PORT% --chip esp8266 --baud 460800 write_flash 0x0 %BIN_FILE% 0x200000 %DATA_FILE%


GOTO END

:ERROR_DATA
echo ERROR: data file does not exist
GOTO END

:ERROR_BIN
echo ERROR: bin file does not exist
GOTO END

:ERROR_PORT
echo ERROR: could not find com port
GOTO END

:END
pause