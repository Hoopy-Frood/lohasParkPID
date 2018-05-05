# lohasParkPID
A PID implementation for LOHAS Park MTR Station

Get MTR next train information for the LOHAS Park MTR Station in HK.  Intented to be used with Raspberry Pi, but any python enabled machine would do.

The MTR Next train information can be accessed from the Android app.  But I found it better to have a display by the door using a low-powered Raspberry Pi with a 3.5" display.  The information is not really public and secured with a keyed hash, but the mechanism can be retrieved from the decompiled MTR APK.

## Installation

Would need the following packages:
* python-tk
* python-imaging-tk
* python-tz
* [pywapi-0.3.8](https://github.com/kapt/pywapi)

