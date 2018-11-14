# MinXSS_Beacon_Decoder
## Overview
A GUI for decoding serial or socket data received with a UHF HAM radio station from the CSIM CubeSat in space. CSIM will be launch November 18th, 2018.

WARNING: This code is not production ready, but I wanted it to be available for the HAM community at launch! Expect bugs! We're working on it!

CSIM will beacon every 16 seconds at 437.250 MHz. The modulation scheme is GFSK. The baud rate will nominally be 9600. The beacons contain health and safety information about the spacecraft. 

This program receives the serial or socket data from MinXSS, interprets it, and displays that interpreted data in human readable formats. For example, you can see real time voltages, currents, temperatures, and spacecraft mode. The telemetry is color coded corresponding to the expected ranges for each telemetry point (green = good, yellow = borderline or warning, red = bad). It also forwards the binary data recorded to the MinXSS team (by default, but this can be disabled with the corresponding toggle). 

All of this code is made open source to hopefully encourage other CubeSat programs to adopt it. (Thanks MinXSS!!!)

The GUI is built with the designer component of [Qt Creator](https://www.qt.io/download) (open source version; it's not necessary to have this unless you want to edit the interface). It uses the [Qt for Python project](https://www.qt.io/qt-for-python) (pyside2 module, available, e.g., [in anaconda](https://anaconda.org/conda-forge/pyside2)) to convert the Qt Designer .ui file into a .py (this is required if you want to run the code directly but not required if you're running the built beacon decoder application). [csim_beacon_decoder.py](csim_beacon_decoder.py) wraps around that GUI code to provide the buttons and text displays with functionality. It uses [connect_port_get_packet.py](connect_port_get_packet.py) to establish a link with the user-specified serial port or TCP/IP socket and then read from it. [csim_parser.py](csim_parser.py) is then fed the binary and interprets the data into a dictionary, which is returned to [csim_beacon_decoder.py](csim_beacon_decoder.py) for display in the GUI. 

Here is what the layout looks like (for MinXSS, CSIM to come.): 
![Example Screenshot of Telemetry](/screenshots/in_operation1_v2.0.2.png)

Data forwarding is to come in future releases. For now, the data is saved to your disk. If you feel so kind, the CSIM team would greatly appreciate data being emailed to mattdhanley@gmail.com. Thanks!

![Example Screenshot of Input / Options](/screenshots/in_operation2_v2.0.2.png)

See the release page for periodic releases of code in a good state: https://github.com/matthewdhanley/CSIM_Beacon_Decoder/releases. 

![Example Screenshot of About](/screenshots/in_operation3_v1.1.0.png)

## How to run from the compiled code (.exe, .app)
1. If you haven't already downloaded [the latest release](https://github.com/matthewdhanley/CSIM_Beacon_Decoder/releases), do so. 
2. Just double click the downloaded .exe or .app! If it gives you issues, try running it as administrator to give it the permissions to write to your disk. In Windows, you can just right click on the application and select "Run As Administrator". In Mac, open a terminal, change directories to where you have the .app, then change directories into the .app/Contents/MacOS/ and type "sudo CSIM_Beacon_DecoderMac". 
3. If you're still having problems, make a new directory in your <username> home folder called "CSIM_Beacon_Decoder". Copy the [input_properties.cfg](input_properties.cfg) file from this MinXSS_Beacon_Decoder codebase into the new folder. Try running again.
4. If it is still not working, create an [issue](https://github.com/matthewdhanley/CSIM_Beacon_Decoder/issues) on this page. 

## How to run from the code directly (Recommended)
1. If you haven't already downloaded a local copy of this codebase, do so. 
2. Open a terminal, navigate to the directory you are storing this codebase, and type: "python csim_beacon_decoder". Note that this code was developed with python 3, so it may not work if you're using python 2.
3. That's it! You should see the UI window pop open and you should be able to interact with it. 

## How to edit interface
1. If you don't already have python > anaconda > pyqt installed, do so. In a terminal, type "conda install pyqt".
2. Open the Qt Designer. It should be in a path like this: /Users/<username>/anaconda/bin/Designer.app
3. Go to File > Open and select [ui_mainWindow.ui](ui_mainWindow.ui) from your local copy of this CSIM_Beacon_Decoder codebase. 
4. Edit away! 
5. Go to File > Save. 
6. Convert the .ui to a .py. To do this, in a Unix terminal, type "./compile_ui.sh" while in the local directory where you have this CSIM_Beacon_Decoder codebase. If you're on Windows, just take a look at the commands in [compile_ui.sh](compile_ui.sh) and run them in your command prompt. 
7. That's it! Next time you run [csim_beacon_decoder.py](csim_beacon_decoder.py), it should show your edits. Note that if you are making edits where you want to change the functionality of the code, you'll need to dive into the corresponding .py files to make those changes as well. 

## How to compile code to executable
1. Get onto the operating system that you want to compile for. The tool we're using (pyinstaller) is not a cross-compiler. That means that if you're on Windows, you can't compile for Mac and vice versa and ditto for Linux. 
2. Test that the code works when you do a normal run from the code directly (see instructions above). 
3. From a terminal window, navigate to the directory where you have your local copy of this codebase. If on Windows, type: "make.bat". If on Mac or Linux, type: "./make.sh". This is just a convenient wrapper script for pyinstaller so you don't have to remember all of the input and output parameters. If it crashes, read the warning messages and respond appropriately. The most likely thing to fail is missing python modules. If that's the reason for failure, in the terminal, just type "pip install" and the name of the module. For example, "pip install pyserial". 

## So you want to modify the code for your own use? Do it from MinXSS! 
1. [Fork the code on github](https://help.github.com/articles/fork-a-repo/).
2. Set up your development environment however you like to interface between your developers local copies and the github server. Or if you don't want to use github, do whatever setup you like. 
3. Edit the code and follow good programming practices with commits, etc. 