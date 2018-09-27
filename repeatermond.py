# repeatermond.py
# Main program

import piplates.DAQCplate as DAQC
import time
import math
import mysql.connector as mariadb
import RPi.GPIO as GPIO
import ConfigParser
import io
import sys

from time import sleep
from os import system

# ./rm_config.py
#import rm_config

__author__     = 'Wyatt Miler, KJ4CTD'
__copyright__  = 'Copyright (c) 2018 Wyatt Miler, KJ4CTD'
__maintainer__ = 'Wyatt Miler, KJ4CTD'
__email__      = 'kj4ctd@wmiler.org'

# Interrupt setup
# NOTE: Not safe to run interupts with callbacks due to MySQL conflicts
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(22, GPIO.RISING, bouncetime=50)
DAQC.enableDINint(0,0,'r')
DAQC.intEnable(0)

# Globals
#TODO kj4ctd Make sure to change these for production
USER = 'pi'
PASSWD = 'wmiler'
DBNAME = 'w4nykMonitor'
ANTS = [450, 300, 200, 100]
ANALOGIO = [0, 1, 2, 3, 4, 5, 6, 7, 8]
DIGIN = [0, 1, 2, 3, 4, 5, 6, 7]
DEBUG=1

mariadb_connection = mariadb.connect(user=USER, password=PASSWD, database=DBNAME)
cursor = mariadb_connection.cursor()
dict_cursor = mariadb_connection.cursor(dictionary=True)

# TODO This needs to be broken out into its own file
# Next two defs are for reading and writing a config file
def rm_write_config():
  config = ConfigParser.RawConfigParser()

  if not config.read('repeatermond.cfg'):
    print('Configuration file \033[93mrepeatermond.cfg\033[0m is not a valid configuration file! Creating defaults.')

  CONFIG = {}
  CONFIG['MYSQLD'] = {}
  CONFIG['MONITOR'] = {}

  try:
    config.add_section('mysqld')
    config.set('mysqld', 'USER', 'pi')
    config.set('mysqld', 'PASSWD', 'wmiler')
    config.set('mysqld', 'DBHOST', 'localhost'),
    config.set('mysqld', 'DBNAME', 'w4nykMonitor')

    config.add_section('monitor')
    config.set('monitor', 'DEBUG', '1')
    config.set('monitor', 'ANTS', '[450, 300, 200, 100]')
    config.set('monitor', 'DIGIN', '[0, 1, 2, 3, 4, 5, 6, 7]')

    with open('repeatermond.cfg', 'wb') as configfile:
      config.write(configfile)
  except ConfigParser.Error, err:
    print "Cannot parse configuration file. %s" %err
    sys.exit('Could not parse configuration file. Exiting...')

def rm_read_config():
  config = ConfigParser.RawConfigParser()

  if not config.read('repeatermond.cfg'):
    sys.exit('Configuration file \033[93mrepeatermond.cfg\033[0m is not a valid configuration file! Exiting...')

  CONFIG = {}
  CONFIG['MYSQLD'] = {}
  CONFIG['MONITOR'] = {}

  try:
    for section in config.sections():
      if section == 'MYSQLD':
        CONFIG['MYSQLD'].update({
          'USER': config.get(section, 'USER'),
          'PASSWD': config.get(section, 'PASSWD'),
          'DBHOST': config.get(section, 'DBHOST'),
          'DBNAME': config.get(section, 'DBNAME')
        })
      elif section == 'MONITOR':
        CONFIG['MONITOR'].update({
          'DEBUG': config.get(section, 'DEBUG'),
          'ANTS': config.get(section, 'ANTS'),
          'DIGIN': config.get(section, 'DIGIN')
        })
  except ConfigParser.Error, err:
    print "Cannot parse configuration file. %s" %err
    sys.exit('Could not parse configuration file. Exiting...')
  return CONFIG

def createDB():
  if DEBUG:
    query2 = """mysql -u {} -p{} --host {} < repeatermond.sql"""
  else:
    query = """mysql -u pi -pwmiler --host localhost < repeatermond.sql"""
  try:
#    system(query.format(USER, PASSWD, DBHOST))
    print("\033[91m query2: {} \033[0m".format(query2))
    system(query)
  except:
    print("\033[91m Error creating db \033[0m".format(err))

def get_calfac(element_size):
  query = """SELECT * FROM  `calibration` WHERE `elementSize` = {} AND `fiveW` IS NOT NULL"""

  try:
    dict_cursor.execute(query.format(element_size))
    row = dict_cursor.fetchone()
  except mariadb.Error as err:
    print("\033[91m Error calfac db \033[0m".format(err))

# TODO return the full calibration factors as needed or wanted, for now, factor at 5W is good enough
  return row['fiveW']

def triggerINT():
  DAQC.setDOUTbit(0,0)
  DAQC.getINTflags(0)
  print("\033[94m _-*xmit triggered!*-_ \033[0m")
  vswr()
  DAQC.clrDOUTbit(0,0)

# TODO Add get_calfac to calc_vswr
def calc_vswr(ant,f,r):
  calfac = get_calfac(100)
  revcalfac = get_calfac(100)

  f=abs(DAQC.getADC(0,f))
  r=abs(DAQC.getADC(0,r))
# TODO For normalizing elements when true test rig is ready
#  f=f-calfac
#  r=r-revcalfac
  x=abs(1 + math.sqrt(safe_div(r,f)))
  y=abs(1 - math.sqrt(safe_div(r,f)))
  swr=round(safe_div(x,y), 3)
  if swr > 3.0:
    print("Ant Height: {} SWR:  \033[91m {} \033[0m".format(ant,swr))
  else:
    print("Ant Height: {} SWR:  \033[92m {} \033[0m".format(ant,swr))
  return swr

def vswr():
  for ant in ANTS:
    if ant == 450:
      swr_450=calc_vswr(ant,0,1)
    elif ant == 300:
      swr_300=calc_vswr(ant,2,3)
    elif ant == 200:
      swr_200=calc_vswr(ant,4,5)
    elif ant == 100:
      swr_100=calc_vswr(ant,6,7)

  query = """INSERT INTO `swr` (`id`, `unix_time`, `fourfifty`, `threeHundred`, `twoHundred`, `oneHundred`) VALUES (NULL, CURRENT_TIMESTAMP, {}, {}, {}, {})"""

  try:
    cursor.execute(query.format(swr_450, swr_300, swr_200, swr_100))
    mariadb_connection.commit()
  except mariadb.Error as err:
    mariadb_connection.rollback()
    print("\033[91m Error swr db \033[0m".format(err))

def safe_div(x,y):
  if y==0: return 1
  return x/y

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

def eval_din(din):
  if din == 0:
    val = "\033[93m Closed \033[0m"
  else:
    val = "\033[92m Open \033[0m"
  return val

def db_din():
  for din in DIGIN:
    if din == 0:
      din_0 = DAQC.getDINbit(0,0)
      val = eval_din(din_0)
      print("Din {}: {}".format(0,val))
    elif din == 1:
      din_1 = DAQC.getDINbit(0,1)
      val = eval_din(din_1)
      print("Din {}: {}".format(1,val))
    elif din == 2:
      din_2 = DAQC.getDINbit(0,2)
      val = eval_din(din_2)
      print("Din {}: {}".format(2,val))
    elif din == 3:
      din_3 = DAQC.getDINbit(0,3)
      val = eval_din(din_3)
      print("Din {}: {}".format(3,val))
    elif din == 4:
      din_4 = DAQC.getDINbit(0,4)
      val = eval_din(din_4)
      print("Din {}: {}".format(4,val))
    elif din == 5:
      din_5 = DAQC.getDINbit(0,5)
      val = eval_din(din_5)
      print("Din {}: {}".format(5,val))
    elif din == 6:
      din_6 = DAQC.getDINbit(0,6)
      val = eval_din(din_6)
      print("Din {}: {}".format(6,val))
    elif din == 7:
      din_7 = DAQC.getDINbit(0,7)
      val = eval_din(din_7)
      print("Din {}: {}".format(7,val))

  query = """INSERT INTO `digInput` (`id`, `unix_time`, `dig0`, `dig1`, `dig2`, `dig3`, `dig4`, `dig5`, `dig6`, `dig7`) VALUES (NULL, CURRENT_TIMESTAMP, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"""

  try:
    cursor.execute(query.format(din_0, din_1, din_2, din_3, din_4, din_5, din_6, din_7))
    mariadb_connection.commit()
  except mariadb.Error as err:
    mariadb_connection.rollback()
    print("\033[91m Error digInput db \033[0m {}".format(err))

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

def eval_analog(aio):
  if aio < 0:
    aio = 0.0
  return aio

def db_analog():
  calfac = get_calfac(100)
  for aio in ANALOGIO:
    if aio == 0:
      aio_0 = DAQC.getADC(0,0)
      aio_0 = aio_0 - calfac
      aio_0 = eval_analog(aio_0)
      print("Analog In {}: {}vDC".format(aio, aio_0))
    elif aio == 1:
      aio_1 = DAQC.getADC(0,1)
      aio_1 = aio_1 - calfac
      aio_1 = eval_analog(aio_1)
      print("Analog In {}: {}vDC".format(aio, aio_1))
    elif aio == 2:
      aio_2 = DAQC.getADC(0,2)
      aio_2 = aio_2 - calfac
      aio_2 = eval_analog(aio_2)
      print("Analog In {}: {}vDC".format(aio, aio_2))
    elif aio == 3:
      aio_3 = DAQC.getADC(0,3)
      aio_3 = aio_3 - calfac
      aio_3 = eval_analog(aio_3)
      print("Analog In {}: {}vDC".format(aio, aio_3))
    elif aio == 4:
      aio_4 = DAQC.getADC(0,4)
      aio_4 = aio_4 - calfac
      aio_4 = eval_analog(aio_4)
      print("Analog In {}: {}vDC".format(aio, aio_4))
    elif aio == 5:
      aio_5 = DAQC.getADC(0,5)
      aio_5 = aio_5 - calfac
      aio_5 = eval_analog(aio_5)
      print("Analog In {}: {}vDC".format(aio, aio_5))
    elif aio == 6:
      aio_6 = DAQC.getADC(0,6)
      aio_6 = aio_6 - calfac
      aio_6 = eval_analog(aio_6)
      print("Analog In {}: {}vDC".format(aio, aio_6))
    elif aio == 7:
      aio_7 = DAQC.getADC(0,7)
      aio_7 = aio_7 - calfac
      aio_7 = eval_analog(aio_7)
      print("Analog In {}: {}vDC".format(aio, aio_7))
    elif aio == 8:
      aio_8 = DAQC.getADC(0,8)
      aio_8 = aio_8 - calfac
      aio_8 = eval_analog(aio_8)
      print("Analog In {}: {}vDC adcRef".format(aio, aio_8))

  query = """INSERT INTO `analogInput` (`id`, `unix_time`, `analog0`, `analog1`, `analog2`, `analog3`, `analog4`, `analog5`, `analog6`, `analog7`, `analog8`) VALUES (NULL, CURRENT_TIMESTAMP, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"""

  try:
    cursor.execute(query.format(aio_0, aio_1, aio_2, aio_3, aio_4, aio_5, aio_6, aio_7, aio_8))
    mariadb_connection.commit()
  except mariadb.Error as err:
    mariadb_connection.rollback()
    print("\033[91m Error analogInput db \033[0m".format(err))

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
    print("\033[92mDB: database and tables exist \033[0m")
  else:
    print("\033[91mDB: no tables, creating database \033[0m")
    createDB()

#  CONFIG = rm_read_config()
#  print("DEBUG Config: {}".format(CONFIG))
  print(rm_read_config())

  while True:
    if GPIO.event_detected(22):
      triggerINT()
    clr_all()
    print(time.ctime())
    # Two red flashes denotes start of cycle
    blink_red()
    blink_red()
    print("INT flags: {}".format(DAQC.getINTflags(0)))
    db_analog()
    db_din()

    # End of cycle
    blink_red()
    blink_red()
    clr_all()
    if DEBUG:
      get_calfac(100)
      print("\033[91mDEBUG sleep 10s\033[0m")
      sleep(10)
    else:
# sleep for 30 minutes
      sleep(900)
except KeyboardInterrupt:
  cursor.close()
  mariadb_connection.close()
  GPIO.cleanup()
