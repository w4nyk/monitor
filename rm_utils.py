# rm_utils.py
# Various utility functions

import piplates.DAQCplate as DAQC
import ConfigParser
import math
import time
from time import sleep

__author__     = 'Wyatt Miler, KJ4CTD'
__copyright__  = 'Copyright (c) 2018 Wyatt Miler, KJ4CTD'
__maintainer__ = 'Wyatt Miler, KJ4CTD'
__email__      = 'kj4ctd@wmiler.org'

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

def eval_analog(aio):
  if aio < 0:
    aio = 0.0
  return aio
