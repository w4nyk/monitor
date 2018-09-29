# rm_config.py
# Read/write config file repeatermond.cfg

import ConfigParser
import io
import sys

__author__     = 'Wyatt Miler, KJ4CTD'
__copyright__  = 'Copyright (c) 2018 Wyatt Miler, KJ4CTD'
__maintainer__ = 'Wyatt Miler, KJ4CTD'
__email__      = 'kj4ctd@wmiler.org'

def rm_write_config():
  config = ConfigParser.RawConfigParser()

  if not config.read('repeatermond.cfg'):
    print('Configuration file \033[93mrepeatermond.cfg\033[0m is not a valid configuration file! Creating defaults.')

  CONFIG = {}
  CONFIG['MYSQLD'] = {}
  CONFIG['MONITOR'] = {}

  try:
    config.add_section('MYSQLD')
    config.set('MYSQLD', 'USER', 'pi')
    config.set('MYSQLD', 'PASSWD', 'wmiler')
    config.set('MYSQLD', 'DBHOST', 'localhost')
    config.set('MYSQLD', 'DBNAME', 'w4nykMonitor')

    config.add_section('MONITOR')
    config.set('MONITOR', 'DEBUG', '1')
    config.set('MONITOR', 'ANTS', '450, 300, 200, 100')
    config.set('MONITOR', 'ANALOGIO', '0, 1, 2, 3, 4, 5, 6, 7, 8')
    config.set('MONITOR', 'DIGIN', '0, 1, 2, 3, 4, 5, 6, 7')
    config.set('MONITOR', 'ELEMENTS', '100, 1, 100, 1, 100, 1, 100, 1')

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
          'USER': config.get('MYSQLD', 'USER'),
          'PASSWD': config.get('MYSQLD', 'PASSWD'),
          'DBHOST': config.get('MYSQLD', 'DBHOST'),
          'DBNAME': config.get('MYSQLD', 'DBNAME')
        })
      elif section == 'MONITOR':
        CONFIG['MONITOR'].update({
          'DEBUG': config.get('MONITOR', 'DEBUG'),
          'ANTS': config.get('MONITOR', 'ANTS'),
          'ANALOGIO': config.get('MONITOR', 'ANALOGIO'),
          'DIGIN': config.get('MONITOR', 'DIGIN'),
          'ELEMENTS': config.get('MONITOR', 'ELEMENTS')
        })
  except ConfigParser.Error, err:
    print "Cannot parse configuration file. %s" %err
    sys.exit('Could not parse configuration file. Exiting...')
  return CONFIG
