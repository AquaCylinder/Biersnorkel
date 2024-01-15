# Biersnorkel
Een biersnorkel met app die verbind via bluetooth en kivy

![De biersnorkel](https://github.com/[AquaCylinder]/[Biersnorkel]/blob/Biersnorkel.jpg?raw=true)

Preparations:
install python via https://www.python.org/downloads/
-latest tested stable version: 3.11.6

install Kivy on your machine:
latest tested stable version: 2.2.1
go to: https://kivy.org/doc/stable/gettingstarted/installation.html for more info

open CMD (Administrator mode) and:
- type in: python -m pip install --upgrade pip setuptools virtualenv
	NOTE: depending on your system, instead of "python" you may need to use "py" instead
inside CMD, navigate to a folder you want to store a virtual envoirnement (venv)
example: navigate by typing in: cd C:\Users\"your_username"\Documents\School\kivy_venv_files
- type in: python -m venv kivy_venv   and click enter
- type in: kivy_venv\Scripts\activate    and click enter
- type in: python -m pip install "kivy[full]" kivy_examples    and click enter

you can store your code files on a different location than your venv files
example in C:\users\"your_username"\Documents\python_files

everytime when starting up, you will need to reïnitialize the venv by typing in the CMD:
	- navigating to the correct folder (using "cd C:\username\folder")
	- enable the script "kivy_venv\Scripts\activate"
	- navigate to the place your files are stored (using "cd C:\username\other_folder")
	keep your CMD active while using Python, when CMD is closed, you will need to repeat above steps

install firebaseAdmin:
- in CMD type: pip install firebase-admin

install SimplyPyBLE:
- in CMD type: pip install simplepyble

after install:
- store all files (firebase and logo's) in the same directory as your main files are stored



installing arduino-IDE components
add u8g2 library (by oliver) in arduino-IDE

In your Arduino IDE, go to File> Preferences (or use Ctrl+comma shortcut)
Enter the following into the “Additional Board Manager URLs” field: https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
click "OK"
Open the Boards Manager. Go to Tools > Board > Boards Manager…
Search for ESP32 and press install button for the “ESP32 by Espressif Systems“:

install the CP210x USB to UART bridge VCP drivers
https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
select the right download for your OS

test the install:
Select your Board in Tools > Board menu. select "ESP32 dev board"
select a port
Open the following example under File > Examples and choose an example
upload and check if it uploaded correctly



Following idea's for improving this product:

in the app:
- language support
- multiple themes
- app support for IOS and Android
- offline mode with local storage buffer
- login screen
- improving connection screen
- search people in scoreboard
- other scoreboard filters
- location support
- bluetooth instead of BLE


physical improvements:
- isolate ESP32 chip itself (ditch dev board kit)
- battery
- pcb with screen and functional buttons

extra unknown error improvements:
- fix unknown WINRT errors






