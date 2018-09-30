# repeatermond.py
# Main program

__author__     = 'Wyatt Miler, KJ4CTD'
__copyright__  = 'Copyright (c) 2018 Wyatt Miler, KJ4CTD'
__maintainer__ = 'Wyatt Miler, KJ4CTD'
__email__      = 'kj4ctd@wmiler.org'


import piplates.DAQCplate as DAQC
import time
import math
import mysql.connector as mariadb
import RPi.GPIO as GPIO
import ConfigParser
import io
import sys
import logging

from time import sleep
from os import system

# ./rm_config.py
# Contains our config file utils
import rm_config
# ./rm_utils.py
# Contains various utility functions
import rm_utils

config = rm_config.rm_read_config()

# Interrupt setup
# NOTE: Not safe to run interupts with callbacks due to MySQL conflicts
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(22, GPIO.RISING, bouncetime=50)
DAQC.enableDINint(0,0,'r')
DAQC.intEnable(0)

# Globals
# These are set up in repeatermond.cfg
USER = config['MYSQLD']['USER']
PASSWD = config['MYSQLD']['PASSWD']
DBHOST = config['MYSQLD']['DBHOST']
DBNAME = config['MYSQLD']['DBNAME']

ANTS = [int(str_val) for str_val in config['MONITOR']['ANTS'].split(',')]
ANALOGIO = [int(str_val) for str_val in config['MONITOR']['ANALOGIO'].split(',')]
DIGIN = [int(str_val) for str_val in config['MONITOR']['DIGIN'].split(',')]
ELEMENTS = [int(str_val) for str_val in config['MONITOR']['ELEMENTS'].split(',')]
DEBUG = config['MONITOR']['DEBUG']

# Set up the logger
logging.basicConfig(filename='repeatermond.log', format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger()


# Make the initial database connection
try:
  logger.debug("DB: Initial connection")
  mariadb_connection = mariadb.connect(user=USER, password=PASSWD, host=DBHOST, database=DBNAME)
  cursor = mariadb_connection.cursor()
  dict_cursor = mariadb_connection.cursor(dictionary=True)
except mariadb.Error as err:
  logger.error("DB: Initial connection FAILED: {}".format(err))
  print("\033[91mDB: Error inital connection\033[0m".format(err))

def createDB():
  """Initializes the DB with default tables.

  Uses config file keywords under the MYSQLD heading
  """
  query = """mysql -u {} -p{} -h {} -D {} < repeatermond.sql"""
  try:
    logger.debug("DB: createDB")
    system(query.format(USER, PASSWD, DBHOST, DBNAME))
  except:
    logger.error("DB: createDB FAILED: {}".format(err))
    print("\033[91mError creating db \033[0m".format(err))

# TODO This needs to fail gracefully if no calibration data available
# Get_calfac(I/O port) or should this really be element size??
def get_calfac(element_size):
  """Gets the calibration factors from the database for the given element size.
  """
  logger.debug("get_calfac")
  query = """SELECT * FROM  `calibration` WHERE `elementSize` = {} AND `fiveW` IS NOT NULL"""

# Grab the element from db and grab the cal data
#  for ele in ELEMENTS:
#    if ele == 100:

  try:
    logger.debug("get_calfac: {}".format(element_size))
    dict_cursor.execute(query.format(element_size))
  except mariadb.Error as err:
    logger.error("DB: get_calfac FAILED: {}".format(err))
    print("\033[91mDB: execute error calfac {}\033[0m".format(err))

  try:
    logger.debug("get_calfac: row")
    row = dict_cursor.fetchone()
  except mariadb.Error as err:
    logger.error("DB: get_calfac FAILED: {}".format(err))
    print("\033[91mDB: fetchone error calfac {}\033[0m".format(err))

# TODO return the full calibration factors as needed or wanted, for now, factor at 5W is good enough
  if row == None:
    logger.debug("DB: get_calfac FAILED: row == None")
    print("\033[91mPlease run the calibration program 'rm_calibrate'\033[0m")
  else:
    return row['fiveW']

def triggerINT():
  """Callback rountine when a Digital Input has been triggered.
  """
  logger.debug("triggerINT")

  DAQC.setDOUTbit(0,0)
  DAQC.getINTflags(0)
  print("\033[94m _-*xmit triggered!*-_ \033[0m")
  vswr()
  DAQC.clrDOUTbit(0,0)

# TODO Add get_calfac to calc_vswr
# calc_vswr(antenna, forward i/o port, reverse i/o port)
def calc_vswr(ant,f,r):
  """Calculates the Voltage Standing Wave Ratio (VSWR) for a given antenna.

  Arguments:
  ant -- The antenna height (aquired from the config file)
  f -- Analog I/O pin on the DAQCplate board to read
  r -- Analog I/O pin on the DAQCplate board to read
  """

#  fwdcalfac = get_calfac(f)
#  revcalfac = get_calfac(r)

  f=abs(DAQC.getADC(0,f))
  r=abs(DAQC.getADC(0,r))
# TODO For normalizing elements when true test rig is ready
#  f=f-fwdcalfac
#  r=r-revcalfac
  x=abs(1 + math.sqrt(rm_utils.safe_div(r,f)))
  y=abs(1 - math.sqrt(rm_utils.safe_div(r,f)))
  swr=round(rm_utils.safe_div(x,y), 3)
  if swr > 3.0:
    logger.warning("calc_vswr: Ant Height: {} SWR:  \033[91m {} \033[0m".format(ant,swr))
    print("Ant Height: {} SWR:  \033[91m {} \033[0m".format(ant,swr))
  else:
    print("Ant Height: {} SWR:  \033[92m {} \033[0m".format(ant,swr))
  return swr

def vswr():
  """Fancy looping switch to calculate vswr and preps a SQL statement for db insertion."""

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
    logger.error("DB: vswr FAILED: {}".format(err))
    mariadb_connection.rollback()
    print("\033[91m Error swr db {}\033[0m".format(err))

def db_din():
  """Scans the Digital Input pins for status."""

  for din in DIGIN:
    if din == 0:
      din_0 = DAQC.getDINbit(0,0)
      val = rm_utils.eval_din(din_0)
      print("Din {}: {}".format(0,val))
    elif din == 1:
      din_1 = DAQC.getDINbit(0,1)
      val = rm_utils.eval_din(din_1)
      print("Din {}: {}".format(1,val))
    elif din == 2:
      din_2 = DAQC.getDINbit(0,2)
      val = rm_utils.eval_din(din_2)
      print("Din {}: {}".format(2,val))
    elif din == 3:
      din_3 = DAQC.getDINbit(0,3)
      val = rm_utils.eval_din(din_3)
      print("Din {}: {}".format(3,val))
    elif din == 4:
      din_4 = DAQC.getDINbit(0,4)
      val = rm_utils.eval_din(din_4)
      print("Din {}: {}".format(4,val))
    elif din == 5:
      din_5 = DAQC.getDINbit(0,5)
      val = rm_utils.eval_din(din_5)
      print("Din {}: {}".format(5,val))
    elif din == 6:
      din_6 = DAQC.getDINbit(0,6)
      val = rm_utils.eval_din(din_6)
      print("Din {}: {}".format(6,val))
    elif din == 7:
      din_7 = DAQC.getDINbit(0,7)
      val = rm_utils.eval_din(din_7)
      print("Din {}: {}".format(7,val))

  query = """INSERT INTO `digInput` (`id`, `unix_time`, `dig0`, `dig1`, `dig2`, `dig3`, `dig4`, `dig5`, `dig6`, `dig7`) VALUES (NULL, CURRENT_TIMESTAMP, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"""

  try:
    cursor.execute(query.format(din_0, din_1, din_2, din_3, din_4, din_5, din_6, din_7))
    mariadb_connection.commit()
  except mariadb.Error as err:
    logger.error("DB: db_din FAILED: {}".format(err))
    mariadb_connection.rollback()
    print("\033[91m Error digInput db \033[0m {}".format(err))

def db_analog():
  """Reads the Analog I/O pins, adjusts for the calibration factor and preps a SQL statement for insertion into the database. """
#  calfac = get_calfac(100)
  calfac = 0
  for aio in ANALOGIO:
    if aio == 0:
      aio_0 = DAQC.getADC(0,0)
      aio_0 = aio_0 - calfac
      aio_0 = rm_utils.eval_analog(aio_0)
      print("Analog In {}: {}vDC".format(aio, aio_0))
    elif aio == 1:
      aio_1 = DAQC.getADC(0,1)
      aio_1 = aio_1 - calfac
      aio_1 = rm_utils.eval_analog(aio_1)
      print("Analog In {}: {}vDC".format(aio, aio_1))
    elif aio == 2:
      aio_2 = DAQC.getADC(0,2)
      aio_2 = aio_2 - calfac
      aio_2 = rm_utils.eval_analog(aio_2)
      print("Analog In {}: {}vDC".format(aio, aio_2))
    elif aio == 3:
      aio_3 = DAQC.getADC(0,3)
      aio_3 = aio_3 - calfac
      aio_3 = rm_utils.eval_analog(aio_3)
      print("Analog In {}: {}vDC".format(aio, aio_3))
    elif aio == 4:
      aio_4 = DAQC.getADC(0,4)
      aio_4 = aio_4 - calfac
      aio_4 = rm_utils.eval_analog(aio_4)
      print("Analog In {}: {}vDC".format(aio, aio_4))
    elif aio == 5:
      aio_5 = DAQC.getADC(0,5)
      aio_5 = aio_5 - calfac
      aio_5 = rm_utils.eval_analog(aio_5)
      print("Analog In {}: {}vDC".format(aio, aio_5))
    elif aio == 6:
      aio_6 = DAQC.getADC(0,6)
      aio_6 = aio_6 - calfac
      aio_6 = rm_utils.eval_analog(aio_6)
      print("Analog In {}: {}vDC".format(aio, aio_6))
    elif aio == 7:
      aio_7 = DAQC.getADC(0,7)
      aio_7 = aio_7 - calfac
      aio_7 = rm_utils.eval_analog(aio_7)
      print("Analog In {}: {}vDC".format(aio, aio_7))
    elif aio == 8:
      aio_8 = DAQC.getADC(0,8)
      aio_8 = aio_8 - calfac
      aio_8 = rm_utils.eval_analog(aio_8)
      print("Analog In {}: {}vDC adcRef".format(aio, aio_8))

  query = """INSERT INTO `analogInput` (`id`, `unix_time`, `analog0`, `analog1`, `analog2`, `analog3`, `analog4`, `analog5`, `analog6`, `analog7`, `analog8`) VALUES (NULL, CURRENT_TIMESTAMP, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"""

  try:
    cursor.execute(query.format(aio_0, aio_1, aio_2, aio_3, aio_4, aio_5, aio_6, aio_7, aio_8))
    mariadb_connection.commit()
  except mariadb.Error as err:
    logger.error("DB: db_analog FAILED: {}".format(err))
    mariadb_connection.rollback()
    print("\033[91m Error analogInput db \033[0m".format(err))

# TODO kj4ctd Main loop, cleanup and make it production quality
# Do a loop every 10 mins or so
def main():
  try:
    """Main program loop."""
    logger.debug("Main loop start")

    cursor.execute("SHOW TABLES LIKE 'swr'")
    result = cursor.fetchone()
    if result:
      print("\033[92mDB: database and tables exist \033[0m")
    else:
      print("\033[91mDB: no tables, creating database \033[0m")
      createDB()

    while True:
      if GPIO.event_detected(22):
        triggerINT()
      rm_utils.clr_all()
      print(time.ctime())
      # Two red flashes denotes start of cycle
      rm_utils.blink_red()
      rm_utils.blink_red()
      print("INT flags: {}".format(DAQC.getINTflags(0)))
      db_analog()
      db_din()

      # Two red flashes denotes end of cycle
      rm_utils.blink_red()
      rm_utils.blink_red()
      rm_utils.clr_all()
      if DEBUG:
        print("\033[91mDEBUG sleep 10s\033[0m")
        sleep(10)
      else:
  # sleep for 30 minutes
        sleep(900)
  except KeyboardInterrupt:
    cursor.close()
    mariadb_connection.close()
    GPIO.cleanup()

if __name__ == '__main__':
  main()
