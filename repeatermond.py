# repeatermond.py
# Main program

import piplates.DAQCplate as DAQC
import time
import math
import mysql.connector as mariadb
import RPi.GPIO as GPIO
from time import sleep
from os import system

# Interrupt setup
# NOTE: Not safe to run interupts with callbacks due to MySQL conflicts
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(22, GPIO.RISING, bouncetime=50)
DAQC.enableDINint(0,0,'r')
DAQC.intEnable(0)

# Globals
#TODO kj4ctd Make sure to change these for production
mariadb_connection = mariadb.connect(user='pi', password='wmiler', database='w4nykMonitor')
cursor = mariadb_connection.cursor()

def createDB():
  query = """mysql -u pi -pwmiler --host localhost < repeatermond.sql"""
  try:
    system(query)
  except:
    print("\033[91m Error creating db \033[0m".format(err))

def triggerINT():
  DAQC.setDOUTbit(0,0)
  DAQC.getINTflags(0)
  print("\033[94m _-*xmit triggered!*-_ \033[0m")
  vswr(450)
  sleep(0.05)
  vswr(300)
  sleep(0.05)
  vswr(200)
  sleep(0.05)
  vswr(100)
  sleep(0.05)
  DAQC.clrDOUTbit(0,0)

def vswr(ant):
  if ant == 450:
    f=abs(DAQC.getADC(0,0))
    r=abs(DAQC.getADC(0,1))
    query = """INSERT INTO `swr` (`id`, `unix_time`, `fourfifty`, `threeHundred`, `twoHundred`, `oneHundred`) VALUES (NULL, CURRENT_TIMESTAMP, {}, NULL, NULL, NULL)"""
  elif ant == 300:
    f=abs(DAQC.getADC(0,2))
    r=abs(DAQC.getADC(0,3))
    query = """INSERT INTO `swr` (`id`, `unix_time`, `fourfifty`, `threeHundred`, `twoHundred`, `oneHundred`) VALUES (NULL, CURRENT_TIMESTAMP, NULL, {}, NULL, NULL)"""
  elif ant == 200:
    f=abs(DAQC.getADC(0,4))
    r=abs(DAQC.getADC(0,5))
    query = """INSERT INTO `swr` (`id`, `unix_time`, `fourfifty`, `threeHundred`, `twoHundred`, `oneHundred`) VALUES (NULL, CURRENT_TIMESTAMP, NULL, NULL, {}, NULL)"""
  elif ant == 100:
    f=abs(DAQC.getADC(0,6))
    r=abs(DAQC.getADC(0,7))
    query = """INSERT INTO `swr` (`id`, `unix_time`, `fourfifty`, `threeHundred`, `twoHundred`, `oneHundred`) VALUES (NULL, CURRENT_TIMESTAMP, NULL, NULL, NULL, {})"""

  x=abs(1 + math.sqrt(r/f))
  y=abs(1 - math.sqrt(r/f))

# TODO: kj4ctd Catch divide by 0, give it something else while in testing
  if y <= 0:
    y = 0.1

  if x <= 0:
    x = 0.1

  swr=round(x/y, 3)
  if swr > 3.0:
    print("Ant Height: {} SWR:  \033[91m {} \033[0m".format(ant,swr))
  else:
    print("Ant Height: {} SWR:  \033[92m {} \033[0m".format(ant,swr))

  try:
    cursor.execute(query.format(swr))
    mariadb_connection.commit()
  except mariadb.Error as err:
    mariadb_connection.rollback()
    print("\033[91m Error swr db \033[0m".format(err))

def blink_red():
  DAQC.setLED(0,0)
  sleep(0.05)
  DAQC.clrLED(0,0)
  sleep(0.05)

def blink_green():
  DAQC.setLED(0,1)
  sleep(0.05)
  DAQC.clrLED(0,1)
  sleep(0.05)

def blink_dio(c):
  DAQC.setDOUTbit(0,c)
  sleep(0.1)
  DAQC.clrDOUTbit(0,c)
  sleep(0.1)

def clr_all():
  DAQC.clrLED(0,0)
  DAQC.clrLED(0,1)
  DAQC.clrDOUTbit(0,0)
  DAQC.clrDOUTbit(0,1)
  DAQC.clrDOUTbit(0,2)
  DAQC.clrDOUTbit(0,3)
  DAQC.clrDOUTbit(0,4)
  DAQC.clrDOUTbit(0,5)
  DAQC.clrDOUTbit(0,6)
  print("\r\n")

def print_din(c):
  val = DAQC.getDINbit(0,c)

#TODO kj4ctd Base this on c and only update that column in the table. Python is messy, switch would've been better
  if c == 0:
    query = """INSERT INTO `digInput` (`id`, `unix_time`, `dig0`, `dig1`, `dig2`, `dig3`, `dig4`, `dig5`, `dig6`, `dig7`) VALUES (NULL, CURRENT_TIMESTAMP, '{}', '1', '1', '1', '1', '1', '1', '1')"""
  elif c == 1:
    query = """INSERT INTO `digInput` (`id`, `unix_time`, `dig0`, `dig1`, `dig2`, `dig3`, `dig4`, `dig5`, `dig6`, `dig7`) VALUES (NULL, CURRENT_TIMESTAMP, '1', '{}', '1', '1', '1', '1', '1', '1')"""
  elif c == 2:
    query = """INSERT INTO `digInput` (`id`, `unix_time`, `dig0`, `dig1`, `dig2`, `dig3`, `dig4`, `dig5`, `dig6`, `dig7`) VALUES (NULL, CURRENT_TIMESTAMP, '1', '1', '{}', '1', '1', '1', '1', '1')"""
  elif c == 3:
    query = """INSERT INTO `digInput` (`id`, `unix_time`, `dig0`, `dig1`, `dig2`, `dig3`, `dig4`, `dig5`, `dig6`, `dig7`) VALUES (NULL, CURRENT_TIMESTAMP, '1', '1', '1', '{}', '1', '1', '1', '1')"""
  elif c == 4:
    query = """INSERT INTO `digInput` (`id`, `unix_time`, `dig0`, `dig1`, `dig2`, `dig3`, `dig4`, `dig5`, `dig6`, `dig7`) VALUES (NULL, CURRENT_TIMESTAMP, '1', '1', '1', '1', '{}', '1', '1', '1')"""
  elif c == 5:
    query = """INSERT INTO `digInput` (`id`, `unix_time`, `dig0`, `dig1`, `dig2`, `dig3`, `dig4`, `dig5`, `dig6`, `dig7`) VALUES (NULL, CURRENT_TIMESTAMP, '1', '1', '1', '1', '1', '{}', '1', '1')"""
  elif c == 6:
    query = """INSERT INTO `digInput` (`id`, `unix_time`, `dig0`, `dig1`, `dig2`, `dig3`, `dig4`, `dig5`, `dig6`, `dig7`) VALUES (NULL, CURRENT_TIMESTAMP, '1', '1', '1', '1', '1', '1', '{}', '1')"""
  else:
    query = """INSERT INTO `digInput` (`id`, `unix_time`, `dig0`, `dig1`, `dig2`, `dig3`, `dig4`, `dig5`, `dig6`, `dig7`) VALUES (NULL, CURRENT_TIMESTAMP, '1', '1', '1', '1', '1', '1', '1', '{}')"""

  try:
    cursor.execute(query.format(val))
    mariadb_connection.commit()
  except mariadb.Error as err:
    mariadb_connection.rollback()
    print("\033[91m Error digInput db \033[0m {}".format(err))

  if val == 0:
    val = "\033[93m Closed \033[0m"
  else:
    val = "\033[92m Open \033[0m"
  print("Din {}: {}".format(c,val))


def print_vdc():
  val=DAQC.getADC(0,8)
  print("Power (adref): {}vDC".format(val))

#TODO kj4ctd Only update that column in the table, Need to use UPDATE?
  query = """INSERT INTO `analogInput` (`id`, `unix_time`, `analog0`, `analog1`, `analog2`, `analog3`, `analog4`, `analog5`, `analog6`, `analog7`, `analog8`) VALUES (NULL, CURRENT_TIMESTAMP, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, {})"""
  try:
    cursor.execute(query.format(val))
    mariadb_connection.commit()
  except mariadb.Error as err:
    mariadb_connection.rollback()
    print("\033[91m Error vdc db \033[0m".format(err))

# TODO kj4ctd Pull calibrartion factor (calfac) from database instead of directly
def print_chan(c, calfac):
  val = DAQC.getADC(0,c)
  val = val - calfac
  if val < 0:
    val = 0.0
  print("Analog In {}: {}vDC".format(c, val))

#TODO kj4ctd Base this on c and only update that column in the table
  if c == 0:
    query = """INSERT INTO `analogInput` (`id`, `unix_time`, `analog0`, `analog1`, `analog2`, `analog3`, `analog4`, `analog5`, `analog6`, `analog7`, `analog8`) VALUES (NULL, CURRENT_TIMESTAMP, '{}', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0')"""
  elif c == 1:
    query = """INSERT INTO `analogInput` (`id`, `unix_time`, `analog0`, `analog1`, `analog2`, `analog3`, `analog4`, `analog5`, `analog6`, `analog7`, `analog8`) VALUES (NULL, CURRENT_TIMESTAMP, '0.0', '{}', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0')"""
  elif c == 2:
    query = """INSERT INTO `analogInput` (`id`, `unix_time`, `analog0`, `analog1`, `analog2`, `analog3`, `analog4`, `analog5`, `analog6`, `analog7`, `analog8`) VALUES (NULL, CURRENT_TIMESTAMP, '0.0', '0.0', '{}', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0')"""
  elif c == 3:
    query = """INSERT INTO `analogInput` (`id`, `unix_time`, `analog0`, `analog1`, `analog2`, `analog3`, `analog4`, `analog5`, `analog6`, `analog7`, `analog8`) VALUES (NULL, CURRENT_TIMESTAMP, '0.0', '0.0', '0.0', '{}', '0.0', '0.0', '0.0', '0.0', '0.0')"""
  elif c == 4:
    query = """INSERT INTO `analogInput` (`id`, `unix_time`, `analog0`, `analog1`, `analog2`, `analog3`, `analog4`, `analog5`, `analog6`, `analog7`, `analog8`) VALUES (NULL, CURRENT_TIMESTAMP, '0.0', '0.0', '0.0', '0.0', '{}', '0.0', '0.0', '0.0', '0.0')"""
  elif c == 5:
    query = """INSERT INTO `analogInput` (`id`, `unix_time`, `analog0`, `analog1`, `analog2`, `analog3`, `analog4`, `analog5`, `analog6`, `analog7`, `analog8`) VALUES (NULL, CURRENT_TIMESTAMP, '0.0', '0.0', '0.0', '0.0', '0.0', '{}', '0.0', '0.0', '0.0')"""
  elif c == 6:
    query = """INSERT INTO `analogInput` (`id`, `unix_time`, `analog0`, `analog1`, `analog2`, `analog3`, `analog4`, `analog5`, `analog6`, `analog7`, `analog8`) VALUES (NULL, CURRENT_TIMESTAMP, '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '{}', '0.0', '0.0')"""
  else:
    query = """INSERT INTO `analogInput` (`id`, `unix_time`, `analog0`, `analog1`, `analog2`, `analog3`, `analog4`, `analog5`, `analog6`, `analog7`, `analog8`) VALUES (NULL, CURRENT_TIMESTAMP, '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '{}', '0.0')"""

  try:
    cursor.execute(query.format(val))
    mariadb_connection.commit()
  except mariadb.Error as err:
    mariadb_connection.rollback()
    print("\033[91m Error analogInput db \033[0m".format(err))

# TODO kj4ctd Main loop, cleanup and make it production quality
# Do a loop every 10 mins or so
try:
  cursor.execute("SHOW TABLES LIKE 'swr'")
  result = cursor.fetchone()
  if result:
    print("DB: table exists")
  else:
    print("DB: no table, creating database")
    createDB()

  while True:
    if GPIO.event_detected(22):
      triggerINT()
    clr_all()
    print(time.ctime())
    # Two red flashes denotes start of cycle
    blink_red()
    blink_red()
    print_vdc()
    print("INT flags: {}".format(DAQC.getINTflags(0)))
    print_chan(0,2.39)
    print_chan(1,0.052)
    print_chan(2,2.44)
    print_chan(3,2.96)
    print_chan(4,2.40)
    print_chan(5,2.46)
    print_chan(6,3.11)
    print_chan(7,3.06)

    print_din(0)
    print_din(1)
    print_din(2)
    print_din(3)
    print_din(4)
    print_din(5)
    print_din(6)
    print_din(7)


    # End of cycle
    clr_all()
    blink_red()
    blink_red()
# sleep for 30 minutes
    sleep(900)
except KeyboardInterrupt:
  cursor.close()
  mariadb_connection.close()
  GPIO.cleanup()
