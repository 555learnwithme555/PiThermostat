#!/usr/bin/python
# Modified 30-Oct-2013
# tng@chegwin.org
# Retrieve: 
# 1: target temperature from a calendar
# 2: current temperature from a TMP102 sensor
# 3: weather from the weather_file (or run weather_script and try again)
#    file is populated by weather-util. See retrieve-weather.sh for details

import sys,time
from sys import path
import redis
import datetime
from time import sleep
import fileinput, re
from processcalendar import parse_calendar
weather_file='/tmp/weather_conditions.txt'
redthis = redis.StrictRedis(host='433board',port=6379, db=0)

def queue_weather(file):
    outside_temp=0
    redthis.set("temperature/weather",0) 
#    print ("Reading weather file %s" % file)
    import fileinput,re
    regex = re.compile(r'\s+Temperature:\s+(\d+) F \((.*)\sC\)')
    for line in fileinput.input(file):
#        print (line)
        line = line.rstrip() 
#        print (line)
        match = regex.search(line)
#        print match
        if match:
            outside_temp = int(match.group(2))
            redthis.set("temperature/weather",outside_temp) 
     

queue_weather(weather_file)