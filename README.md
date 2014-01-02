## bitalino-raspberry pi ##
=============================

BITalino API for interface with Raspberry Pi via UART.

## Prerequisites ##

The UART that is available on the GPIO pins is located at /dev/ttyAMA0 in Linux Raspbian (and possibly in other Linux distributions).

Follow this tutorial to allow you to console into the Raspberry Pi using the external UART:
http://programmingadvent.blogspot.pt/2012/12/raspberry-pi-uart-with-pyserial.html

Below is a summary of the tutorial in advance:

1 - Backup the two files you are going to edit with:

```
sudo cp /boot/cmdline.txt /boot/cmdline.txt.bak
sudo cp /etc/inittab /etc/inittab.bak
```

2 - Use a text editor to remove these two settings from /boot/cmdline.txt:

```
console=ttyAMA0,115200 kgdboc=ttyAMA0,115200
```

3 - Comment the line that mentions ttyAMA0 in /etc/inittab. (place a # at the start of the line)

```
#T0:23:respawn:/sbin/getty -L ttyAMA0 11520 vt100
```

4 - Install Pyserial and RPI.GPIO:

```
sudo apt-get install pySerial
sudo apt-get install RPi.GPIO
```

5 - Run python file examples

```
sudo python BITalinoPiExample.py
```

## Tested on ##
- Linux Raspbian - Raspberry Pi.

## Hardware details: ##
- connect UART_pi (Tx) to UART_bitalino (Rx);
- connect UART_pi (Rx) to UART_bitalino (Tx);
- Connect an additional RPi_GPIO (output - e.g. GPIO.BOARD '16') to the STAT pin (input) of the BITalino;
- See code comments within BITalino.py for additional information.
