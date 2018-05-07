# lohasParkPID
A python implementation for LOHAS Park MTR Station Passenger Information Display (PID)

This simple script retrieves HK MTR next train information for the LOHAS Park Station.  Intented to be used with Raspberry Pi, but any python enabled machine would do.  Its useful to those who lives in LOHAS Park.  Can easily be incorporated into a smart mirror.

The MTR Next train information is already available from MTR Android/iOS app.  I found it useful to have a display by the door using a low-powered Raspberry Pi with a 3.5" display.  The information is not really public and it is secured with a keyed hash but the mechanism can be retrieved from the decompiled MTR APK.  It also contains weather information from Yahoo.

## Installation

Would need the following packages:
* python-tk
* python-imaging-tk
* python-tz
* [pywapi-0.3.8](https://github.com/kapt/pywapi)

