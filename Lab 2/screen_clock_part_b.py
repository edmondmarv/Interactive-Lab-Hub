import time
import subprocess
import digitalio
import board
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
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    #TODO: Lab 2 part D work should be filled in here. You should be able to look in cli_clock.py and stats.py
    # Time is measured in text messages. 
    # It takes about 5 seconds to send a text message. 
    # Therefore, 12 text messages are sent per minute. 
    # This is used to calculate the current time

    hr = subprocess.check_output("date '+%I'", shell=True).decode("utf-8")
    minute = subprocess.check_output("date '+%M'", shell=True).decode("utf-8")
    ttl_minutes = (int(hr) * 60) + int(minute)
    ttl_minutes_disp = subprocess.check_output("echo {}".format(ttl_minutes), shell=True).decode("utf-8")
    ttl_seconds = ttl_minutes * 60
    ttl_seconds_disp = subprocess.check_output("echo {}".format(ttl_seconds), shell=True).decode("utf-8")
    pct_time = (ttl_minutes / 1440) * 100
    pct_time_disp = subprocess.check_output("echo {}".format(round(pct_time,2)), shell=True).decode("utf-8")
    num_text_msgs = ttl_minutes * 12
    #txt_msg_disp = subprocess.check_output("echo {}".format(num_text_msgs), shell=True).decode("utf-8")
    #time_disp = subprocess.check_output("echo {}:{}".format(hr, minute), shell=True).decode("utf-8")

    curr_secs = "Time in secs: {} \n".format(ttl_seconds_disp)
    curr_mins = "Time in mins: {} \n".format(ttl_minutes_disp) 
    curr_pct = "Time as pct: {}% \n".format(pct_time_disp)
    curr_time = "What time is it now?"
    curr_time_disp = "Time Now: {}:{}".format(hr, minute)

    # Write four lines of text.
    y = top
    draw.text((x, y), curr_secs, font=font, fill="#0000FF")
    y += font.getsize(curr_secs)[1]
    draw.text((x, y), curr_mins, font=font, fill="#00FFFF")
    y += font.getsize(curr_mins)[1]
    draw.text((x, y), curr_pct, font=font, fill="#f45b69")
    y += font.getsize(curr_pct)[1]
    draw.text((x, y), curr_time, font=font, fill="#FFFFFF")

    # Display image.
    disp.image(image, rotation)
    time.sleep(0.5)



