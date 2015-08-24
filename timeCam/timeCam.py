import picamera
import math
import time
from datetime import datetime
from astral import Astral
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import shutil
from fractions import Fraction
from images2gif import writeGif
import os

class box:
  def __init__(self):
    self.x = 0
    self.y = 0
    self.w = 0
    self.h = 0

with picamera.PiCamera() as camera:
  camera.resolution = (640, 480)
  camera.framerate = 24
  a = Astral()
  a.solar_depression = 'civil'
  city = a['Pretoria']
  sun = city.sun(date=datetime.now(), local=True)
  
  # datetime.now() is tz unaware, but the sun stuff not
  sunset_dt = sun['sunset'].replace(tzinfo=None)
  sunrise_dt = sun['sunrise'].replace(tzinfo=None)
  now_dt = datetime.now()
  
  tydstring  =      "Tyd Nou: [" + str(now_dt)     + "]\n"
  tydstring += "Sononder-tyd: [" + str(sunset_dt)  + "]\n"
  tydstring +=    "Sonop-tyd: [" + str(sunrise_dt) + "]\n"
  print tydstring
  print "Sukkel"
  
  if ( not ( ( now_dt >= sunrise_dt) and ( now_dt <= sunset_dt) ) ):
    print "Dis donker, so ons laat ekstra lig in vir die kamera."
    '''
      Night time low light settings have long exposure times Settings for
      Low Light Conditions:
      1. Set a frame rate of 1/6 fps, then
      2. Set shutter speed to 6s and
      3. ISO to 800
    '''
    camera.framerate = Fraction(1, 6)
    camera.shutter_speed = 6000000
    camera.exposure_mode = 'off'
    camera.iso = 800
    # Give the camera a good long time to measure AWB
    time.sleep(8)
  else:
    print "Dis dag - ons los die kamera om sy eie ding te doen."
  time.sleep(2)
  camera.capture('nowRaw.jpg')
  file = open('bac/sec', 'r+')
  sec = int(file.readline())
  file.seek(0)
  file.write(str(sec+1))
  file.truncate()
  file.close()
  
  print "Klaar geneem, nou die datumtydstring op jongste foto sit vir die snaaksegyt."
  now = Image.open('nowRaw.jpg')
  draw = ImageDraw.Draw(now)
  draw.rectangle((0, 0, 160, 20), fill="white")
  font = ImageFont.truetype("/usr/share/fonts/truetype/aargMeMatie/Tahoma.ttf", 16)
  draw.text((5, 0), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), (100, 130, 150), font=font)
  shutil.copy2('nowRaw.jpg', 'bac/' + str(sec) + '.jpg')
  now.save('/var/www/now.jpg')
  
  size = box()

  if datetime.now().minute < 15:
    print "Op die uur - vars collage"
    # Draw last x images as one image
    x = 24
    shrink = 2
    columns = 6
    rows = 4
    size.x = 640/shrink
    size.y = 480/shrink
    size.w = size.x
    size.h = size.y
    lastx = Image.new("RGB", (size.w*columns, size.h*rows), "black")
    draw = ImageDraw.Draw(lastx)
    for i, j in enumerate(xrange(sec-(x-1), sec+1, 1)):
      im = Image.open('bac/'+str(j)+'.jpg')
      im.thumbnail((size.w, size.h), Image.ANTIALIAS)
      lastx.paste(im, ((i%columns)*size.x, (i/columns)*size.y))
    lastx.save('/var/www/last24.jpg')
  elif datetime.now().minute >= 30 and datetime.now().minute < 45: 
    print "Op die halfuur - vars gif - maar eers 60 s wag vir jou om te pause as jy daar is"
    sleep(60)
    # Create a gif of the last 24*(60/15)=96 images
    x = 96
    shrink = 2
    size.x = 640/shrink
    size.y = 480/shrink
    size.w = size.x
    size.h = size.y
    images = []
    for i, j in enumerate(xrange(sec-(x-1), sec+1, 1)):
      im = Image.open('bac/'+str(j)+'.jpg')
      im.thumbnail((size.w, size.h), Image.ANTIALIAS)
      images.append(im)
    filename = "/var/www/lastDay.gif"
    writeGif(filename, images, duration=0.2)
  
  print "Alles Klaar!"
