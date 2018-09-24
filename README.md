# Monitor
Monitors antenna systems and logs to a Mariadb (MySQL) database using a [Raspberry pi 3B+](https://www.raspberrypi.org/products/raspberry-pi-3-model-b-plus/) and the DAQCplate from [DAQCplate](https://pi-plates.com/daqcr1/). Results are pushed to [RPI-Monitor](https://rpi-experiences.blogspot.com/) for web display.

## Installation
``` bash
sudo apt-get install mariadb-server
sudo apt-get install libmariadbclient-dev
sudo pip install pi-plates
pip install mysql-connector-python
```

## RPI-Monitor Installation
You will need sudo priviledges to install.

``` bash
sudo apt-get install dirmngr
sudo apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 2C0D3C0F
sudo wget http://goo.gl/vewCLL -O /etc/apt/sources.list.d/rpimonitor.list
sudo apt-get update
sudo apt-get install rpimonitor
sudo /etc/init.d/rpimonitor update
```
Then copy the files from **THIS** repo under config-files/rpimonitor/template/* to /etc/rpimonitor/template/
