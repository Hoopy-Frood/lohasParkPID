#!/usr/bin/python

import sys
import os
import Tkinter as tk
from PIL import Image, ImageTk
import time
import tkFont
import config #local config file
import requests
import string
import json
import urllib
import threading
import pywapi
import re
from datetime import datetime
from datetime import timedelta
import hashlib
import pytz



color_ds_blue = "#483D8B"
color_bg_blue = "#020546"
color_gold = "#FFD700"
color_red = "#FF0000"
color_sea_green = "#2E8B57"

color_bg = '#020B5B'


disp_units = "metric"
#disp_units = "imperial"
zip_code = 'HKXX0075'

# Show degree F symbol using magic unicode char in a smaller font size.
# The variable uniTmp holds a unicode character that is either DegreeC or DegreeF.
# Yep, one unicode character is has both the letter and the degree symbol.
if disp_units == 'metric':
	uniTmp = unichr(0x2103)		# Unicode for DegreeC //2103
	windSpeed = ' m/s'
	windScale = 0.277778		# To convert kmh to m/s.
	baroUnits = 'mb'
else:
	uniTmp = unichr(0x2109)		# Unicode for DegreeF
	windSpeed = ' mph'
	windScale = 1.0
	baroUnits = ' "Hg'


news_margin = 60

class Application(tk.Frame):
    #### Initialization
    def __init__(self,master=None):
        tk.Frame.__init__(self, master)


        # make it cover the entire screen
        self.w = self.winfo_screenwidth()
        self.h = self.winfo_screenheight()
        # print "width, height:", self.w, ",", self.h

        
        self.master.overrideredirect(1)
        self.master.configure(background=color_bg, cursor='none')
        self.master.geometry("%dx%d+0+0" % (self.w, self.h))
        self.master.columnconfigure(0, weight=1)
        self.grid()

        self.statusInfo = tk.StringVar()
        self.newsVar = tk.StringVar()
        self.newsScrollMsg = " "
        self.operationHours= False

        # Clock Calculations
        self.rebootTime = datetime.strptime(config.REBOOTTIME,"%H:%M:%S")
        self.rebootTimeLimit = datetime.strptime(config.REBOOTTIME,"%H:%M:%S") + timedelta(seconds=10)
        self.lastTrainTime = datetime.strptime(config.LASTTRAIN,"%H:%M:%S")
        self.firstTrainTime = datetime.strptime(config.FIRSTTRAIN,"%H:%M:%S")


        self.createWidgets()
        #eventlet.sleep()
        #eventlet.monkey_patch()

        self.updateClock()


        self.mapImageList = [None]*12
        self.canvasImageList = [None]*12

        # Routes 10 routes max of 50 stops max
        self.trainDest = [None] *4
        self.trainEta = [None] *4
        self.trainTime = [None] *4
        self.threadcounter = 0

        self.lock = threading.Lock()
        self.hasError = False
        self.errorString = " "

        self.loadImages()

        # initialize display
        self.imagePosition = 0
        self.etaText1 = None
        self.etaText2 = None
        self.etaText3 = None
        self.etaText4 = None
        self.destinationText1 = None 
        self.destinationText2 = None
        self.destinationText3 = None
        self.destinationText4 = None
        self.timeText1 = None
        self.timeText2 = None
        self.timeText3 = None
        self.timeText4 = None
        self.weatherText = ""
        self.wLastUpdate = ''
        self.errCount = 0
        
        
        self.image1 = None
        self.image2 = self.canvasImageList[0]
        self.bgCanvas.move(self.image2,-self.canvas_w,0)
        self.displayIndex = 1 #set next image's index

        # build Query URL
        self.UrlBuilder()


        ## Testing Drawing Route
        #self.routeCanvas = tk.Canvas(self.master,width=1920,height=1080)
        #self.routeCanvas.pack()

        print "getETA"
        self.getEta()
        #self.doScheduleScrolling()

        print "get weather"
        self.updateWeather()

        print "do news"
        self.LoadNews = False
        self.getNews()

        self.isNewsText1Long = False

            
        self.newsPosition = 0
        self.newsText1 = self.newsCanvas.create_text(0,10 , anchor=tk.NW, text=self.newsScrollMsg, font=self.newsFont, fill="white")
        newsText1Tuple = self.newsCanvas.bbox(self.newsText1)
        self.newsText1_w = newsText1Tuple[2] - newsText1Tuple[0]

        if self.newsText1_w > self.w:
            self.isNewsText1Long = True
            self.newsText2 = self.newsCanvas.create_text(self.newsText1_w + news_margin,10 , anchor=tk.NW, text=self.newsScrollMsg, font=self.newsFont, fill="white")
            self.newsPosition = self.newsText1_w + news_margin
                        
        self.scrollNews()
        self.statusInfo.set("")


    #### PID Software Related ######################################################
    #### Restart Program
    def restartProgram(self):
        """Restarts the current program.
        Note: this function does not return. Any cleanup action (like
        saving data) must be done before calling this function."""
        python = sys.executable
        os.execl(python, python, * sys.argv)

    #### Reboot PID Controller
    def rebootPID(self):
        command = "/usr/bin/sudo /sbin/shutdown -r now"
        import subprocess
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output = process.communicate()[0]
        print output


    #### Create all the screen elements
    def createWidgets(self):
        
        if (self.w == 1920):
                # FONTS
            self.bufferFont = tkFont.Font(family='Helvetica',size=15, weight='bold')
            #self.timeFont = tkFont.Font(family='Helvetica', size=20, weight='bold')
            self.routeTitleFont = tkFont.Font(family='Helvetica', size=55, weight='bold')
            self.etaFont = tkFont.Font(family='Helvetica', size=60, weight='bold')
            self.dateFont = tkFont.Font(family='Helvetica', size=30, weight='bold')
            #self.stationNameFont = tkFont.Font(family='Helvetica', size=40, weight='bold')
            self.timeFont = tkFont.Font(family='Helvetica', size=55, weight='bold')
            self.statusFont = tkFont.Font(family='Helvetica', size=20)
            self.newsFont = tkFont.Font(family='Helvetica', size=40, weight='bold')
            self.padx = 15
            self.starty = 40
            self.yIncrement = 120
            self.startx = 20
            self.xETA = 600
            self.news_canvas_w = 1920
            self.news_canvas_h = 90 
            self.canvas_w = 1920
            self.canvas_h = 752
            self.top_canvas_w = 1920
            self.top_canvas_h = 238
            self.dx = 2 #must be 1920's multiple
            self.scrollSpeed = 10
        elif (self.w == 320):
            self.bufferFont = tkFont.Font(family='Helvetica',size=2, weight='bold')
            #self.timeFont = tkFont.Font(family='Helvetica', size=20, weight='bold')
            self.routeTitleFont = tkFont.Font(family='Helvetica', size=14, weight='bold')
            self.etaFont = tkFont.Font(family='Helvetica', size=14, weight='bold')
            self.dateFont = tkFont.Font(family='Helvetica', size=10, weight='bold')
            #self.stationNameFont = tkFont.Font(family='Helvetica', size=40, weight='bold')
            self.timeFont = tkFont.Font(family='Helvetica', size=14, weight='bold')
            self.statusFont = tkFont.Font(family='Helvetica', size=9)
            self.newsFont = tkFont.Font(family='Helvetica', size=12, weight='bold')
            self.padx = 2
            self.starty = 6
            self.yIncrement = 30
            self.startx = 3
            self.xETA = 100
            self.news_canvas_w = 320
            self.news_canvas_h = 30
            self.canvas_w = 320
            self.canvas_h = 125
            self.top_canvas_w = 320
            self.top_canvas_h = 40
            self.dx = 1 #must be 1920's multiple
            self.scrollSpeed = 20
        
            
        # Labels
        #self.topCanvasLabel = tk.Canvas(self,width=top_canvas_w, height=top_canvas_h,background=color_bg, highlightthickness=0)
        self.topMarginLabel = tk.Label(self, text="", font=self.bufferFont,bg = color_bg,fg="white")
        self.quitButton = tk.Button(self, text='X',command=self.endApplication,anchor=tk.W,  font=self.dateFont, relief=tk.FLAT,
                         bg = color_bg, activebackground=color_bg, borderwidth=0, highlightthickness=0, fg=color_bg)
        self.dateLabel = tk.Label(self, text="Dec 10", anchor=tk.SE,justify=tk.RIGHT,font=self.dateFont, bg = color_bg, fg="white", padx=self.padx)
        if (config.TEST):
            self.routeLabel = tk.Label(self, text=config.STATIONNAMETEST, anchor=tk.W,justify=tk.LEFT,font=self.routeTitleFont, bg = color_bg,fg="white", padx=self.padx)
        else:
            self.routeLabel = tk.Label(self, text=config.STATIONNAME, anchor=tk.W,justify=tk.LEFT,font=self.routeTitleFont, bg = color_bg,fg="white", padx=self.padx)
        self.timeLabel = tk.Label(self, text="4:37 PM", anchor=tk.SE,justify=tk.RIGHT,font=self.timeFont, bg = color_bg,fg="white", padx=self.padx)
        self.separator1 = tk.Label(self, text="", font=self.bufferFont,bg = color_bg,fg="white")
        self.bgCanvas = tk.Canvas(self, width=self.canvas_w, height=self.canvas_h, background=color_bg, highlightthickness=0)
        #self.routeCanvas = tk.Canvas(self, width=canvas_w, height=canvas_h, background=color_bg, highlightthickness=0)
        self.statusLabel = tk.Label(self, textvariable=self.statusInfo, justify=tk.RIGHT, font=self.statusFont,bg = color_bg,fg="yellow", anchor=tk.NE)
        self.newsLabel = tk.Label(self, textvariable=self.newsVar, anchor=tk.NW, font=self.newsFont,bg = color_bg,fg="white")
        self.newsCanvas = tk.Canvas(self, width=self.news_canvas_w, height=self.news_canvas_h, background=color_bg, highlightthickness=0)
        
        # Grid
        if (self.w == 1920):
            self.topMarginLabel.grid(row=0,column=0,columnspan=4, sticky="nsew")
        self.quitButton.grid(row=1, column=0, sticky = "nsew")
        self.dateLabel.grid(row=1,column=1,columnspan=4, sticky="nsew")
        self.routeLabel.grid(row=2,column=0, columnspan =2, sticky="nsew")
        self.timeLabel.grid(row=2,column=2,columnspan=2, sticky="nsew")
        self.bgCanvas.grid(row=3,column=0,columnspan=4, sticky="nsew")
        self.statusLabel.grid(row=5,column=0,columnspan=4,sticky="nsew")
        self.newsCanvas.grid(row=6,column=0,columnspan=4, sticky="nsew")



    #### Load background to RAM
    def loadImages(self):        
        index = 0
        if (self.w == 1920):
            canvasheight = 752
        elif (self.w == 320):
            canvasheight = 125
        else:
            canvasheight = self.w *752 / 1920

        imgpath = config.APPDIR + '0000031.jpg'
        self.mapImageList[index] = ImageTk.PhotoImage(Image.open(imgpath).resize((self.w,canvasheight)))
        self.canvasImageList[index] = self.bgCanvas.create_image(self.canvas_w,0,anchor=tk.NW, image=self.mapImageList[index])

    def formatStopName (self, text):
        formattedText = re.sub("[\(\[].*?[\)\]]", "", text)
        if len(formattedText) > 25:
            formattedText = formattedText[0:22] + "..."
        return formattedText


    def UrlBuilder (self):
        sha1Input = config.SERVICELINE + "|" + config.SERVICESTATION + "|en|" + time.strftime ('%Y-%m-%d') + "|c90vfabc"
        m = hashlib.sha1()
        m.update(sha1Input)
        self.queryUrl = config.SERVICEURLPREFIX + m.hexdigest() + "&line=" + config.SERVICELINE + "&sta=" + config.SERVICESTATION + "&lang=en"
        print "URL IS ", self.queryUrl

    #### ETA Related ###############################################################
    #### Get ETA Worker Thread
    def getEtaCallback(self):
        data = None
        hasError = False
        errorString = ""
        currentThreadCounter = self.threadcounter;
        self.threadcounter += 1;

        print "Enters getEtaCallback : ",  time.strftime ('%H:%M:%S'), " Thread = ", currentThreadCounter

        if self.operationHours == False:
            self.statusInfo.set("Trains not in operation: " + time.strftime ('%m-%d %H:%M:%S'))
            return

        try:

            session = requests.Session()
            session.trust_env = True;
            print "Request start : ",  time.strftime ('%H:%M:%S'), " Thread = ", currentThreadCounter
            
            #increased timeout because this runs in a thread. it will not affect scrolling. maybe we can increase it up to config.DISPLAYUPDATETIME
            r = requests.get(self.queryUrl)
            #r = grequests.get(config.SERVICEURL[url_index]), exception_handler=self.exception, size=5)

            print "Request Return: ",  time.strftime ('%H:%M:%S') , " Thread = ", currentThreadCounter                       
            data = r.json()
            if data is None:
                print "data: BLANK"

            print "data: " , data

            if data['message'] != 'successful':
                print "message is unsuccessful"
            
            downdata = data['data']['TKL-LHP']['DOWN']

            numdata = len(downdata)
            print "Number of Entries: ", numdata

            sysTime = datetime.strptime(data['data']['TKL-LHP']['sys_time'], "%Y-%m-%d %H:%M:%S").strftime ('%m-%d %H:%M:%S')
            
            i=0
            while i < 4:
                if (i > numdata):
                    self.trainDest[i] = ''
                    self.trainEta[i] = ''
                    self.trainDateTimeObj[i] = None
                else:    
                    self.trainDest[i] = downdata[i]['dest']
                    self.trainEta[i] = downdata[i]['ttnt']
                    self.trainTime[i] = datetime.strptime(downdata[i]['time'], "%Y-%m-%d %H:%M:%S").strftime ('%I:%M').lstrip('0') + time.strftime(' %p').lower()
                    print "Route : ", downdata[i]['dest'], "\t ETA : ", downdata[i]['ttnt'], "\tTime: ", self.trainTime[i]
                                
                i += 1
            # while i < numdata
            
                
            
            
            
        except (requests.exceptions.ConnectionError):
            print "Connection Error"
            #self.statusInfo.set("No connection" + time.strftime ('%m/%d %H:%M:%S'))
            errorString = "No connection " + time.strftime ('%m-%d %H:%M:%S')
            hasError = True
        except requests.exceptions.ReadTimeout as err:
            print "ReadTimeout Error: ", (err.args)
            errorString = "Network issue " + time.strftime ('%m-%d %H:%M:%S')
            hasError = True
        except requests.exceptions.Timeout as err:
            print "Timeout Error: ", (err.args)
            errorString = "Network issue " + time.strftime ('%m-%d %H:%M:%S')
            hasError = True
        except ValueError as err:
            print "Value Error: ", (err.args)
            errorString = "Server issue " + time.strftime ('%m-%d %H:%M:%S')
            hasError = True
        except TypeError as err:
            print "Type Error: ", (err.args)
            errorString = "Server issue " + time.strftime ('%m-%d %H:%M:%S')
            hasError = True
        except KeyError as err:
            print "Key Error: ", (err.args)
            errorString = "Server data unavailable " + time.strftime ('%m-%d %H:%M:%S')
            hasError = True
        except UnboundLocalError as err:       # Should be timeout from eventlet
            print "UnboundLocalError:", (err.args)
            errorString = "Network issue " + time.strftime ('%m-%d %H:%M:%S')
            hasError = True

        self.hasError = hasError
        self.errorString = errorString
        
        if self.hasError:
            self.statusInfo.set(self.errorString)
        else:
            self.statusInfo.set("Last Update: " + time.strftime ('%m-%d %H:%M:%S') + " Server Time: " + sysTime)

        self.updateText2()

           
        
    #### Get all ETA information Thread Starter - recursive
    # - Assumes no two URL will have the same route (Second one may replace the first)
    def getEta(self):
        thread1 = threading.Thread(target=self.getEtaCallback)
        thread1.start()


        self.after(config.UPDATETIME_ETA*1000,self.getEta)     

    #### Update ETA
    def updateText2(self):
        routeDisplayIndex = self.displayIndex
        
        destinationString = [None] *4
        etaString = [None]*4
        fillColor = ['white'] * 4
        with self.lock:
            i = 0
            while (i < 4):
                if (self.trainDest[i] == 'NOP'):
                    if (config.TEST):
                        destinationString[i] = 'SM Seaside' #'North Point'
                    else:
                        destinationString[i] = 'North Point'
                elif self.trainDest[i] == 'TIK':
                    if (config.TEST):
                        destinationString[i] = 'SM City Cebu' #'Tiu Keng Leng'
                    else:
                        destinationString[i] = 'Tiu Keng Leng'
                else:
                    destinationString[i] = ''
                
                if (self.trainEta[i] == '0'):
                    etaString[i] = "Leaving"
                    fillColor[i] = "grey"
                elif (self.trainEta[i] == '1'):
                    etaString[i] = "Departing"
                    fillColor[i] = "red"
                else:
                    etaString[i] = self.trainEta[i]
                    if (int(self.trainEta[i]) < 6 ):
                        fillColor[i] = "yellow"
                    else:
                        fillColor[i] = "white"
                
                i += 1
        

        y = self.starty

        self.bgCanvas.delete(self.destinationText1)
        self.bgCanvas.delete(self.etaText1)
        self.bgCanvas.delete(self.timeText1)
        self.destinationText1 = self.bgCanvas.create_text(self.startx,y, anchor=tk.NW, text=destinationString[0], font=self.etaFont, fill=fillColor[0])
        self.etaText1 = self.bgCanvas.create_text(self.w - self.xETA, y, anchor=tk.NE, text=etaString[0], font=self.etaFont, fill=fillColor[0])
        self.timeText1 = self.bgCanvas.create_text(self.w - self.startx, y, anchor=tk.NE, text=self.trainTime[0], font=self.etaFont, fill=fillColor[0])
        y += self.yIncrement
        self.bgCanvas.delete(self.destinationText2)
        self.bgCanvas.delete(self.etaText2)
        self.bgCanvas.delete(self.timeText2)
        self.destinationText2 = self.bgCanvas.create_text(self.startx, y, anchor=tk.NW, text=destinationString[1], font=self.etaFont, fill=fillColor[1])
        self.etaText2 = self.bgCanvas.create_text(self.w -self.xETA, y, anchor=tk.NE, text=etaString[1], font=self.etaFont, fill=fillColor[1])
        self.timeText2 = self.bgCanvas.create_text(self.w -self.startx, y, anchor=tk.NE, text=self.trainTime[1], font=self.etaFont, fill=fillColor[1])
        y += self.yIncrement
        self.bgCanvas.delete(self.destinationText3)
        self.bgCanvas.delete(self.etaText3)
        self.bgCanvas.delete(self.timeText3)
        self.destinationText3 = self.bgCanvas.create_text(self.startx, y, anchor=tk.NW, text=destinationString[2], font=self.etaFont, fill=fillColor[2])
        self.etaText3 = self.bgCanvas.create_text(self.w - self.xETA, y, anchor=tk.NE, text=etaString[2], font=self.etaFont, fill=fillColor[2])
        self.timeText3 = self.bgCanvas.create_text(self.w - self.startx, y, anchor=tk.NE, text=self.trainTime[2], font=self.etaFont, fill=fillColor[2])
        y += self.yIncrement
        self.bgCanvas.delete(self.destinationText4)
        self.bgCanvas.delete(self.etaText4)
        self.bgCanvas.delete(self.timeText4)
        
        self.destinationText4 = self.bgCanvas.create_text(self.startx, y, anchor=tk.NW, text=destinationString[3], font=self.etaFont, fill=fillColor[3])
        self.etaText4 = self.bgCanvas.create_text(self.w - self.xETA, y, anchor=tk.NE, text=etaString[3], font=self.etaFont, fill=fillColor[3])
        self.timeText4 = self.bgCanvas.create_text(self.w - self.startx, y, anchor=tk.NE, text=self.trainTime[3], font=self.etaFont, fill=fillColor[3])
        self.bgCanvas.update()



    #### NEWS Related ##############################################################
    #### Scroll News - Recursive    
    def scrollNews(self):
        dy = 0  
        if self.isNewsText1Long:
            self.newsPosition -= self.dx
            self.newsCanvas.move(self.newsText1, -self.dx, dy)
            self.newsCanvas.move(self.newsText2, -self.dx, dy)
            self.newsCanvas.update()

            if self.newsPosition < 0:
                temp = self.newsText1
                self.newsText1 = self.newsText2
                tups = self.newsCanvas.bbox(self.newsText1)
                w = tups[2] - tups[0]
                
                if w > self.canvas_w:
                    # new announcement is handled here
                    msg = ""
                    with self.lock:
                        msg = self.newsScrollMsg
                    self.newsText2 = self.newsCanvas.create_text(w + news_margin,10 , anchor=tk.NW, text=msg, font=self.newsFont, fill="white")
                    self.newsPosition = w + news_margin
                else:
                    self.isNewsText1Long = False
                    
                self.newsCanvas.delete(temp)
        else:
             # change from announcements
            if self.LoadNews:
                # create new text outside the canvas
                msg = ""
                with self.lock:
                    msg = self.newsScrollMsg
                self.newsText2 = self.newsCanvas.create_text(self.canvas_w + news_margin,10 , anchor=tk.NW, text=msg, font=self.newsFont, fill="white")
                self.newsPosition = self.canvas_w + news_margin
                                    
                self.isNewsText1Long = True

        self.LoadNews = False
             
        self.newsCanvas.after(self.scrollSpeed,self.scrollNews)
    
    #### Get News Worker Thread
    def getNewsCallback(self):
        tempnews = ""
        with self.lock:
            oldnews = self.newsScrollMsg
        print "Enters getNewsCallback :",  time.strftime ('%H:%M:%S')

        
        tempnews = "  " + self.weatherText
        
        if config.NEWSURL != '':
            try:
                print "News URL : ", config.NEWSURL
                r = requests.get(config.NEWSURL,verify=False,timeout=15)
                data = r.json()
                if data is not None:
                    print data
                    numdata = len(data)
                    x =0
                    while x < numdata:
                        if 'news' in data[x]:
                            if tempnews:
                                tempnews = tempnews + " | " + data[x]["news"]
                            else:
                                tempnews = "  " + data[x]["news"]
                        elif 'announcement' in data[x]:
                            if tempnews:
                                tempnews = tempnews + " | " + data[x]["announcement"]
                            else:
                                tempnews = "  " +  data[x]["announcement"]
                                                
                        x+=1
                            
            except (requests.exceptions.ConnectionError):
                print "Connection Error"
            except requests.exceptions.ReadTimeout as err:
                print "ReadTimeout Error:", (err.args)
            except requests.exceptions.Timeout as err:
                print "Timeout Error:", (err.args)
            except ValueError as err:
                print (err.args)
            except TypeError as err:
                print (err.args)
            except UnboundLocalError as err:       # Should be timeout from eventlet
                print "UnboundLocalError:", (err.args)

        with self.lock:
            self.newsScrollMsg = tempnews
                    
            if oldnews != tempnews:
                self.LoadNews = True
        
    #### Get News Thread starter - recursive
    def getNews(self):
        thread1 = threading.Thread(target=self.getNewsCallback)
        thread1.start()  # Start a thread for every getNews

        self.after(config.UPDATETIME_NEWS*1000,self.getNews)



  	####################################################################
    # the PYWAPI seems very inaccurate should try open weather map instead
    # https://codereview.stackexchange.com/questions/131371/script-to-print-weather-report-from-openweathermap-api
    def updateWeather(self):
        # Use Weather.com for source data.
        cc = 'current_conditions'
        f = 'forecasts'
        weather = { cc:{ f:1 }}  # Init to something.
    
        # This is where the magic happens. 
        try:
            self.weather = pywapi.get_weather_from_weather_com( zip_code, units=disp_units )
            weather = self.weather
        except:
            print "Error getting update from weather.com"
            self.errCount += 1
            return
    
        try:

            if ( weather[cc]['last_updated'] != self.wLastUpdate ):
                self.wLastUpdate = weather[cc]['last_updated']
            #print "New Weather Update: " + self.wLastUpdate
            location = weather[cc]['station']
            temperature = string.lower( weather[cc]['temperature'] )+ uniTmp
            condition = weather[cc]['text']
            #self.feels_like = string.lower( w[cc]['feels_like'] )
            #self.wind_speed = string.lower( w[cc]['wind']['speed'] )
            #self.baro = string.lower( w[cc]['barometer']['reading'] )
            #self.wind_dir = string.upper( w[cc]['wind']['text'] )        self.dx = 2 #must be 1920's multiple        self.dx = 2 #must be 1920's multiple
            humidity = string.upper( weather[cc]['humidity'] )  + "%" + unichr(0x1d3f) + unichr(0x1d34)
            #self.vis = string.upper( w[cc]['visibility'] )
            #self.gust = string.upper( w[cc]['wind']['gust'] )
            #self.wind_direction = string.upper( w[cc]['wind']['direction'] )

            utc = pytz.utc
            utcSunrise = utc.localize(datetime.strptime(weather[f][0]['sunrise'], '%I:%M %p'))
            utcSunset  = utc.localize(datetime.strptime(weather[f][0]['sunset'], '%I:%M %p'))
            local = pytz.timezone("Asia/Hong_Kong")
            localSunrise = utcSunrise.astimezone(local)
            localSunset = utcSunset.astimezone(local)
            rainChance = weather[f][0]['day']['chance_precip'] + "%rain"
            if ( weather[f][0]['high'] == 'N/A' ):
    			tempHigh = '--'
            else:	
				tempHigh = weather[f][0]['high']
            tempLow = weather[f][0]['low']

            self.errCount = 0

    
        except KeyError:
            print "KeyError -> Weather Error"
            self.statusInfo = "KeyError -> Weather Error"
            '''if self.errCount >= 15:
                self.temp = '??'
                self.wLastUpdate = ''
            '''
            return False
        except ValueError:
            print "ValueError -> Weather Error"
            self.statusInfo = "ValueError -> Weather Error"

        self.weatherText = temperature + " | " + humidity + " | " + condition + " | " + rainChance  + " | " + tempLow + "-" + tempHigh + uniTmp # + " | SRise " + utcSunrise.strftime("%I:%M%p").lstrip('0').lower() + " | SSet " + utcSunset.strftime("%I:%M%p").lstrip('0').lower()
        print "Weather: ", self.weatherText

        self.after (1800000, self.updateWeather) 

    #### Clock Related ############################################################
    #### Update Clock - recursive
    def updateClock(self):

        curTime = datetime.strptime(time.strftime("%H:%M:%S"),"%H:%M:%S")
	

        if (curTime > self.lastTrainTime) & (curTime < self.firstTrainTime):
            print "Off Operation Hours"
            self.operationHours= False

            if (curTime > self.rebootTime) & (curTime < self.rebootTimeLimit):
                print "Rebooting ... "
                self.rebootPID()
        else:
            self.operationHours= True

        curDay = time.strftime ('%b %-d')

        if curDay != self.dateLabel["text"]:
            self.dateLabel["text"] = curDay
            self.UrlBuilder()

        curTime = time.strftime ('%I:%M:%S').lstrip('0') + time.strftime(' %p').lower()

        if curTime != self.timeLabel["text"]:
            self.timeLabel["text"] = curTime

        self.timeLabel.after (500, self.updateClock)

    #### Quit Application
    def endApplication(self):
        self.quit()

#### Start Applicaiton
app = Application()
app.master.title('LOHAS Park Station PID')

app.mainloop()
