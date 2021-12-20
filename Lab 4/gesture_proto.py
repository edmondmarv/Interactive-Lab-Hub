# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
from adafruit_apds9960.apds9960 import APDS9960
import urllib.request
import json
import pandas as pd
import time
import subprocess
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

i2c = board.I2C()

apds = APDS9960(i2c)
apds.enable_proximity = True
apds.enable_gesture = True

# Uncomment and set the rotation if depending on how your sensor is mounted.
# apds.rotation = 270 # 270 for CLUE

def _weather_pull():

    # Variables Config
    # Geo List: Manhattan: (40.7777, -73.966)
    points_url = "https://api.weather.gov/points/{},{}".format('40.7777', '-73.966')
    features = ['temperature']
    grid_json_dict = {}
    grid_df_dict = {}

    # Data Download & Parsing
    with urllib.request.urlopen(points_url) as url:
        points_data = json.loads(url.read().decode())
        grid_url = points_data['properties']['forecastGridData']
        with urllib.request.urlopen(grid_url) as url:
            grid_data = json.loads(url.read().decode())
            for feature in features:
                # Create dictionary of weather data => { Feature: Weather Data }
                # E.g.: { apparentTemperature: [ { validTime': '2021-05-12T13:00:00+00:00/PT12H', 'value': 19.444444444444443 } ] }
                grid_json_dict[feature] = grid_data['properties'][feature]['values']
                # Dictionary conversion to DataFrame; Back to Dictionary
                grid_df_dict[feature] = pd.DataFrame(grid_json_dict[feature])
                # Convert temperature value from degrees C to degress F
                if 'temp' in feature.lower():
                    degrees_c = grid_df_dict[feature]['value']
                    degrees_f = (degrees_c * 9/5) + 32
                    grid_df_dict[feature]['value_f'] = degrees_f

    return(grid_df_dict[feature]['value_f'])




while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    
    gesture = apds.gesture()

    hr = subprocess.check_output("date '+%I'", shell=True).decode("utf-8")
    minute = subprocess.check_output("date '+%M'", shell=True).decode("utf-8")
    old_ttl_minutes = 0
    new_ttl_minutes = (int(hr) * 60) + int(minute)
    last_updated = new_ttl_minutes - old_ttl_minutes
    last_updated_shell = subprocess.check_output("echo {}".format(last_updated), shell=True).decode("utf-8")

    if gesture:
        hr = subprocess.check_output("date '+%I'", shell=True).decode("utf-8")
        minute = subprocess.check_output("date '+%M'", shell=True).decode("utf-8")
        old_ttl_minutes = (int(hr) * 60) + int(minute)
        last_updated = 0
        last_updated_shell = subprocess.check_output("echo {}".format(last_updated), shell=True).decode("utf-8")

        temp_data = _weather_pull()
        curr_temp = temp_data.at[temp_data.index[-1]]
        curr_temp_shell = subprocess.check_output("echo {}".format(curr_temp), shell=True).decode("utf-8")

        temp_disp = "Current Temp: {} \n".format(curr_temp_shell)
        last_disp = "Last Updated: {} mins ago \n".format(last_updated_shell)

        print(temp_disp)
        print(last_disp)

        # Write four lines of text.
        y = top
        draw.text((x, y), temp_disp, font=font, fill="#FFFFFF")
        y += font.getsize(temp_disp)[1]
        draw.text((x, y), last_disp, font=font, fill="#FFFFFF")

        # Display image.
        disp.image(image, rotation)
    time.sleep(0.5)