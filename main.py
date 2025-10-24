# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2017 James DeVito for Adafruit Industries
# SPDX-License-Identifier: MIT

# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

import subprocess
import time

import busio
from board import SCL, SDA
from PIL import Image, ImageDraw, ImageFont

import adafruit_ssd1306

# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
font = ImageFont.truetype("fonts/JetBrainsMonoNL-Medium.ttf", 12)

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)


def run_cmd(cmd):
    return subprocess.check_output(cmd, shell=True).decode("utf-8").strip()


while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Shell scripts for system monitoring from here:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load

    HOST = run_cmd("hostname")
    IP = run_cmd("hostname -I | awk '{print $1}'")

    WIFI_RATE = run_cmd(
        "iw dev wlan0 link | awk '/signal/ {print $2 \" dBm\"}'")

    SSH_STATUS = run_cmd("systemctl is-active ssh")

    # Conta quantos usuários estão conectados via SSH
    USERS_CONNECTED = run_cmd("who | grep -c 'pts/' || echo 0")

    SSID = run_cmd("iwgetid -r")  # retorna só o SSID

    # Write four lines of text.
    draw.text((x, top + 0), "Host: " + HOST, font=font, fill=255)
    draw.text((x, top + 10), "IP: " + IP, font=font, fill=255)
    draw.text((x, top + 20), "Wi-fi: " + WIFI_RATE, font=font, fill=255)
    draw.text((x, top + 30), "SSH: " + SSH_STATUS, font=font, fill=255)
    draw.text((x, top + 40), "users: " + USERS_CONNECTED, font=font, fill=255)
    draw.text((x, top + 50), "SSID: " + SSID, font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.show()
    time.sleep(0.1)
