# repeatermond.py
# Main program
import piplates.DAQCplate as DAQC
import time
import math
import mysql.connector as mariadb

from time import sleep

mariadb_connection = mariadb.connect(user='pi', password='wmiler', database='w4nykMonitor')
cursor = mariadb_connection.cursor()

def vswr(ant):
  if ant == 450:
    f=abs(DAQC.getADC(0,0))
    r=abs(DAQC.getADC(0,1))
  elif ant == 300:
    f=abs(DAQC.getADC(0,2))
    r=abs(DAQC.getADC(0,3))
  elif ant == 200:
    f=abs(DAQC.getADC(0,4))
    r=abs(DAQC.getADC(0,5))

  x=abs(1 + math.sqrt(r/f))
  y=abs(1 - math.sqrt(r/f))

  # TODO: kj4ctd Catch divide by 0, give it something else while in testing
  if y <= 0:
    y = 0.1

  swr=round(x/y, 3)
  print("Ant Height: {} SWR: {}".format(ant,swr))

def blink_red():
  DAQC.setLED(0,1)
  sleep(0.05)
  DAQC.clrLED(0,1)
  sleep(0.05)

  def blink_green():
  DAQC.setLED(0,0)
  sleep(0.05)
  DAQC.clrLED(0,0)
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
  if val == 0:
    val = "Closed"
  else:
    val = "Open"
  print("Din {}: {}".format(c,val))

#TODO kj4ctd Base this on c and only update that column in the table
  query = """INSERT INTO `digInput` (`id`, `unix_time`, `dig0`, `dig1`, `dig2`, `dig3`, `dig4`, `dig5`, `dig6`, `dig7`) VALUES (NULL, CURRENT_TIMESTAMP, '1', '1', '0', '0', '0', '1', '0', '1')"""

def print_vdc():
  val=DAQC.getADC(0,8)
  print("Power: {}vDC".format(val))

def print_chan(c, calfac):
  val = DAQC.getADC(0,c)
  val = val - calfac
  if val < 0:
    val = 0.0
  print("Analog In {}: {}vDC".format(c, val))

while True:
  clr_all()
  print(time.ctime())
  blink_red()
  blink_red()
  print_vdc()
  vswr(450)
  vswr(300)
  vswr(200)
  print_chan(0,2.39)
  print_chan(1,0.052)
  print_chan(2,2.44)
  print_chan(3,2.96)
  print_chan(4,2.40)
  print_chan(5,2.46)
  print_chan(6,3.11)
  print_chan(7,3.06)
  print("INT flags: {}".format(DAQC.getINTflags(0)))
  blink_green()

  blink_red()
  print_din(0)
  blink_dio(0)
  print_din(1)
  blink_dio(1)
  print_din(2)
  blink_dio(2)
  print_din(3)
  blink_dio(3)
  print_din(4)
  blink_dio(4)
  print_din(5)
  blink_dio(5)
  print_din(6)
  blink_dio(6)
  print_din(7)

  blink_green()
  blink_green()
  clr_all()
  sleep(5)


cursor.close()
mariadb_connection.close()
