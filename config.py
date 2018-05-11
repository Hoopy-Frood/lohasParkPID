# SM SEASIDE CITY CEBU (PID 1)

# ID of this PID
PID_ID = "0100"

TEST = False

# IMPORTANT - NEED TO EQUAL THE TIME IN pidconfig.json
LASTUPDATETIME = "2017-11-01 04:30 PM"

# Station Name Title
STATIONNAMETEST = "SM Seaside City Cebu"
STATIONNAME = "LOHAS Park Station"



# PID Title to display
ROUTEHEADINGTODISPLAY = ["Northbound to", "Southbound to"]
ROUTETEXTTODISPLAY = ["Parkmall (11)", "Lawaan Terminal - Talisay (22)"]

# Station ID to identify self in route map
STATIONID = "01"
STATIONIDALT = ""

# The URL of the Fleet Management Information Server specific to the current station
CONFIGURL = ''

# URL to getStopDepartures or getStopArrivals information
# builds URL in app using sha1.  Reverse engineer from "next train apk" using APK Studio.  Code is in TravelInfoController.smali
## SHA1 input: TKL|LHP|en|2017-11-03|c90vfabc
SERVICEURLPREFIX = 'https://mavmapp1044.azurewebsites.net/reverse_proxy/NT_v2/NTAppModule/getSchedule.php?key='
SERVICELINE = "TKL"
SERVICESTATION = 'LHP'

#SERVICEURL = "https://mavmapp1044.azurewebsites.net/reverse_proxy/NT_v2/NTAppModule/getSchedule.php?key=8cef7dfa19b3c7b2ffa8c30a50f1175ec1ae8e7d&line=TKL&sta=LHP&lang=en" #20171103
            # "https://mavmapp1044.azurewebsites.net/reverse_proxy/NT_v2/NTAppModule/getSchedule.php?key=37eeb593d2c84f33fc028054e84ad363129c8e17&line=TKL&sta=LHP&lang=en" #20171101
            # "https://mavmapp1044.azurewebsites.net/reverse_proxy/NT_v2/NTAppModule/getSchedule.php?key=0BD1BA0FA55EDB6A7D435691CC066908C843C723&line=TKL&sta=LHP&lang=en" #20171102
            # "https://mavmapp1044.azurewebsites.net/reverse_proxy/NT_v2/NTAppModule/getSchedule.php?key=8cef7dfa19b3c7b2ffa8c30a50f1175ec1ae8e7d&line=TKL&sta=LHP&lang=en" #20171103
# For Departing Terminal - Show bus on route map returning to the current stop
# Seems pretty impossible to do without knowing where is the bus on the route. Guessimate from straight line distance leads to lots of errors especially for SMCC where the route turns around
# If route not departing terminal, leave ''
#RETURNSERVICEURL = ["http://122.54.22.110/api/?act=getStopArrivals&p1=01&version=2"]
#RETURNROUTESTOSHOWBUS = ["0000012", "0000021"]

# news URL of the current stop
NEWSURL = ''

# directory for application files
APPDIR = './'


# seconds before the display changes
DISPLAYUPDATETIME = 10

# seconds before the getting ETA info
UPDATETIME_ETA = 15

# seconds before the getting NEWS info
UPDATETIME_NEWS = 60

# seconds before reconnection to Get Route Data
RECONNECTION_TIME = 15


# reboot time set to 3:00 AM if PID is ran overnight (need quotes)
REBOOTTIME = ""

# First train currently is 05:57  PID first gather data at 05:55
FIRSTTRAIN = "05:55:00"  

# Last train currently is 00:48  PID stops gather data at 00:48
LASTTRAIN = "00:48:00"  
