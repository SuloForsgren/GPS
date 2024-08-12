import math
import csv
import datetime
import serial
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7735 as st7735
import time
from datetime import datetime

#GPRMC ==> 
#GPGSV ==>
#GPGLL ==>

class read_data :
    def __init__(self, format) :
        self.format = format


    def read_data(self) :
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
        if line.startswith('$GPRMC'):
            return line
        return None

