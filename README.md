![SleepUINO_Logo_PreDev](https://user-images.githubusercontent.com/48091357/111156537-25298a00-8596-11eb-8726-1fe5cd7bed93.png)
# eep-build-action
eep-build-action is a GitHub Action to build Arduino ESP Projects and create an eep package that can be used with the [ESPEASYFLASHER_2.0](https://github.com/hredan/ESPEASYFLASHER_2.0).
To build the esp binaries, the eep-build-action is using the [arduino-cli](https://github.com/arduino/arduino-cli). The main sketch ino file must be in the root directory of the repository that is using the eep-build-action. If an data directory for a web interface is available, the eep-build-action is using [mklittlefs](https://github.com/earlephilhower/mklittlefs) to create a file system.

For example have a look to the [Example Projects](https://github.com/hredan/eep-build-action#example-projects).

# Inputs of action

The following inputs can be used as `step.with` keys:

| Name               | Type        | Required | Description                                                                                                                          |
|--------------------|-------------|----------|--------------------------------------------------------------------------------------------------------------------------------------|
| `sketch-name`      | String      | true     | Name of the main ino file without the extension ino e.g. "ESP_BLINK".                                                                |
| `sketch-path`      | String      | false    | Path of Sketch (Default '.')                                                                                                         |
| `eep-name`         | String      | false    | Name of eep package (Default ''). If it is an empty string then the sketch-name will be used for the eep-name.                       |
| `core`             | String      | true     | Name of the core. The value can be "esp32" or "esp8266", it depends on the hardware which you are using.                             |
| `board`            | String      | true     | Name of the board. It depends on the board you are using. You can find a list of possible boards [ESP32 Boards](https://github.com/hredan/eep-build-action/wiki/BoardESP32), [ESP8266 Boards](https://github.com/hredan/eep-build-action/wiki/BoardESP8266) in the Wiki. You have to use the name in column "adruino-cli Name".     |
| `libs`             | String      | false    | Libraries that are needed for the build. The Lib names must be comma separated without spaces e.g. `U8g2,RTClib`.                    |
| `cpu-frequency`    | String      | false    | CPU frequency: e.g. 80, 160 or 240. Default is 160.                                                                                   |
| `core-version`     | String      | false    | Version of [esp32](https://github.com/espressif/arduino-esp32) or [esp8266](https://github.com/esp8266/Arduino) core. Default last stable release.                                                                                   |

# Output of action

The action will create a GitHub artifact, that can be downloaded and used with the [ESPEASYFLASHER_2.0](https://github.com/hredan/ESPEASYFLASHER_2.0).

# Example
```
build_ESP8266:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hredan/eep-build-action@v1
        with:
          sketch-name: <your sketch name>
          core: esp8266
          board: d1_mini
```
How the action is working in a GitHub workflow you can have a look to the following Projects:

# Example Projects
## ESP_Blink
[ESP_Blink Workflows](https://github.com/hredan/ESP_Blink/tree/master/.github/workflows)

[ESP_Blink Actions](https://github.com/hredan/ESP_Blink/actions)
## ESP_jQuery_Mobile_Interface Workflows
[ESP_jQuery_Mobile_Interface Workflows](https://github.com/hredan/ESP_jQuery_Mobile_Interface/tree/main/.github/workflows)

[ESP_jQuery_Mobile_Interface Actions](https://github.com/hredan/ESP_jQuery_Mobile_Interface/actions)

# Disclaimer
All this code is released under the GPL, and all of it is to be used at your own risk. If you find any bugs, please let me know via the GitHub issue tracker or drop me an email ([hredan@sleepuino.de](mailto:hredan@sleepuino.de)).
