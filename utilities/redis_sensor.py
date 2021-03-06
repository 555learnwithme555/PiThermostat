#!/usr/bin/python
# Modified 30-Oct-2013
# tng@chegwin.org
# Retrieve: 
# 1: current temperature from a TMP102 sensor
# 2: Send to redis

import sys,time
from sys import path
import datetime
from time import sleep
import re
import redis
from ConfigParser import SafeConfigParser
floattemp = 0

parser = SafeConfigParser()
parser.read('/etc/pithermostat.conf')

redishost=parser.get('redis','broker')
redisport=int(parser.get('redis','port'))
redisdb=parser.get('redis','db')
redistimeout=float(parser.get('redis','timeout'))
redthis=redis.StrictRedis(host=redishost,port=redisport, db=redisdb, socket_timeout=redistimeout)
# Find location from pithermostat.conf
room_location=parser.get('locale','location')
# Will generally be inside/outside
zone_location=parser.get('locale','zone')


time_to_live = 3600
###### IMPORTANT #############
###### How close to comfortable temperature is this sensor
###### determines how much weighting this sensor
###### if used at an extreme point in the house (say cellar), set to 1
###### if used centrally (living room), set to 3 or 4
# Now set in /etc/pithemostat.conf
zone_multiplier=parser.get('locale','multiplier')
#import crankers
import Adafruit_GPIO.I2C as I2C

sensor_name="temperature/"+room_location+"/sensor"
mult_name="temperature/"+room_location+"/multiplier"
zone_name="temperature/"+room_location+"/zone"
#print ("Sensor name is %s" % sensor_name)
#print ("Multiplier name is %s" % mult_name)
#print ("Zone name is %s" % zone_name)

class Tmp102:
  i2c = None

  # Constructor
  def __init__(self, address=0x48, mode=1, debug=False):
    self.i2c = I2C.Device(address, busnum=1)
    self.address = address
    self.debug = debug
    # Make sure the specified mode is in the appropriate range
    if ((mode < 0) | (mode > 3)):
      if (self.debug):
        print "Invalid Mode: Using STANDARD by default"
      self.mode = self.__BMP085_STANDARD
    else:
      self.mode = mode

  def readTemperature(self):
    "Gets the compensated temperature in degrees celcius"
    self.i2c.write8(0, 0x00)                 # Set temp reading mode
    raw = self.i2c.readList(0,2)
    if (self.debug):
        print ("Raw0 = %s, Raw1 = %s" % (raw[0],raw[1]))
    negative = (raw[0] >> 7) == 1
    shift = 4
    if not negative:
        val = (((raw[0] * 256) + raw[1]) >> shift) * 0.0625
    else:
        remove_bit = 0b011111111111
        ti = (((raw[0] * 256) + raw[1]) >> shift)
        # Complement, but remove the first bit.
        ti = float(~ti & remove_bit)
        val = float(float(-(ti))*0.0625)
    if (self.debug):
        print val
    return val

while True:
    try: 
        mytemp = Tmp102(address=0x48)
        floattemp = mytemp.readTemperature()
        #print ("Float temp = %f" % floattemp)
        redthis.set(sensor_name,floattemp)
        redthis.set(mult_name,zone_multiplier)
        redthis.set(zone_name,zone_location)
        redthis.expire(sensor_name,time_to_live)
        redthis.expire(mult_name,time_to_live)
        redthis.expire(zone_name,time_to_live)
    except:
        print ("Unable to retrieve temperature")
    time.sleep(120)
      
