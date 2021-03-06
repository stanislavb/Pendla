#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

import json
from datetime import datetime, date
from time import mktime, time

# Lägg till linux terminal färg-kommandon
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   LIGHTRED = '\033[1;31m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

#api.sl.se/api2/realtimedepartures.<FORMAT>?key=<DIN API NYCKEL>&siteid=<SITEID>&timewindow=<TIMEWINDOW>

### Konfiguration ###

# ID för stationen du vill åka ifrån
stationId = "9507"
# Tidsfönster i minuter
timeWindow = "60"
# Tid i minuter att gå till stationen
walkTime = 16

###

def setStationId(id):
    stationId = id

def setTimeWindow(tw):
    timeWindow = tw

def setWalkTime(t):
    walkTime = t

def getLeaveTime(wt, ct, dt):
    # wt=walktime, ct=currtime, dt=departuretime

    # 1. räkna ut sekunder till avgång
    # 2. subtrahera tiden det tar att gå
    # 3. avrunda uppåt till minuter
    # 4. om minuter < 0, skicka "Nu!"

    timeLeftS = (dt - ct) - wt
    # print "timeLeftS="+str(timeLeftS)

    timeLeftM = int(float(timeLeftS) / 60.0)
    # print "TimeLeftM="+str(timeLeftM)

    if timeLeftM <= 0:
        return color.BOLD + color.RED + '%-7s' % "Nu!" + color.END
    if timeLeftM <= 5:
        return color.BOLD + color.YELLOW + '%-7s' % (str(timeLeftM)+" min") + color.END
    return color.YELLOW + '%-7s' % (str(timeLeftM)+" min") + color.END

def getTrains(apiKey, stationId, timeWindow, walkTime):
    url = "http://api.sl.se/api2/realtimedepartures.json?key="+apiKey+"&siteid="+stationId+"&timewindow="+timeWindow
    #raw json data into 'instanse'
    jsonData = urlopen(url)
    #parsed json data into 'dict'
    jsonParsed = json.load(jsonData)

    # Vi vill bara se pendeltåg
    trains = jsonParsed['ResponseData']['Trains']
    # gör om till sekunder
    walkTime *= 60

    # output enligt nedan
    # "X min (tid/realtid) Destination - Meddelande"

    print color.DARKCYAN+color.BOLD+ "PENDELTÅG"

    # Printa ut lite kolumner
    print color.GREEN+color.BOLD+'%-8s' % "Gå om",
    print '%-8s' % "Avgång",
    print '%-11s' % "Tid",
    print "Destination"
    print

    # print "LatestUpdate="+jsonParsed['ResponseData']['LatestUpdate']
    # print "LatestUpdate(Epoch)="+str(int(mktime(datetime.strptime(jsonParsed['ResponseData']['LatestUpdate'], "%Y-%m-%dT%H:%M:%S").timetuple())))
    # print "DataAge="+str(jsonParsed['ResponseData']['DataAge'])
    # print "currEpochTime="+str(int(time()))
    # print "diff="+str(int(time())-int(mktime(datetime.strptime(jsonParsed['ResponseData']['LatestUpdate'], "%Y-%m-%dT%H:%M:%S").timetuple())))
    # print

    for i in trains:
        # Vi åker bara norrut (2)
        if i['JourneyDirection'] == 2:

            currEpochTime = int(time())
            timeTableEpoch = int(mktime(datetime.strptime(i['TimeTabledDateTime'], "%Y-%m-%dT%H:%M:%S").timetuple()))
            expectedEpoch = int(mktime(datetime.strptime(i['ExpectedDateTime'], "%Y-%m-%dT%H:%M:%S").timetuple()))
            timeTablePretty = datetime.strftime(datetime.strptime(i['TimeTabledDateTime'], "%Y-%m-%dT%H:%M:%S"), "%H:%M")
            ExpectedPretty = datetime.strftime(datetime.strptime(i['ExpectedDateTime'], "%Y-%m-%dT%H:%M:%S"), "%H:%M")

            # Om tiden till tåget går är mindre än tiden det tar att gå
            if (timeTableEpoch-currEpochTime) < walkTime:
                continue

            # if timeTableEpoch != expectedEpoch:
            #     minsLeft = int(math.ceil((float(expectedEpoch) - float(currEpochTime)) / 60))
            # else:
            #     minsLeft = int(math.ceil((float(timeTableEpoch) - float(currEpochTime)) / 60))

            # print str(math.ceil((float(expectedEpoch) - float(currEpochTime)) / 60)) + " minuter kvar"

            # Visa "Gå om"
            print color.END+getLeaveTime(walkTime, currEpochTime, expectedEpoch),

            # Visa "DisplayTime"
            print color.YELLOW + '%-7s' % i['DisplayTime'].encode('utf-8') + color.END,

            # Om realtid matchar tidtabellen
            if timeTableEpoch == expectedEpoch:
                # Visa tabelltid
                print '%-11s' % timeTablePretty,
            # ...Annars printa både tabelltid samt ny tid
            else:
                # Visa tabelltid
                print '%-11s' % (timeTablePretty+"/"+color.RED+ExpectedPretty+color.END),

            # Visa destination
            print color.YELLOW+'%-11s' % i['Destination'].encode('utf-8')+color.END

            # Om det finns avvikelser, printa meddelandet
            if i['Deviations']:
                print color.DARKCYAN+"- " + i['Deviations'][0]['Text'][:80]+color.END

    print
