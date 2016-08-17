
A.  prepare functional https://github.com/pfalcon/esp-open-sdk
B.  prepare https://github.com/micropython/micropython 
    you need to prepare esp8266 'folder' separatedly and have compiler from esp-open-sdk in your $PATH
    in micropython/esp8266: make PORT=/dev/ttyUSB0 deploy
C.  I suggest http://docs.micropython.org/en/v1.8/esp8266/esp8266/quickref.html#networking to setup wifi
D.  use https://github.com/micropython/webrepl to copy files into micropython
    on the device, you need to properly setup webrepl and "import webrepl; webrepl.start"
    http://docs.micropython.org/en/v1.8/esp8266/esp8266/quickref.html#webrepl-web-browser-interactive-prompt
