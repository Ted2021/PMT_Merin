import serial
import time
import glob
import os
import sys
import subprocess
from generalfunc import *

#USBのポートを参照する関数
def get_serial_num():
   def serialnum(tnum):
      command = 'system_profiler SPUSBDataType | grep -B 3'
      target = 'Location ID: '
      
      #stream = os.popen(command + ' ' + tnum)
      #output = stream.read()
      stream = subprocess.Popen(command.split()+[tnum], stdout=subprocess.PIPE, stderr=subprocess.PIPE)      #subprocessを用いてshellを実行
      output = stream.stdout.read() # 標準出力の場合
      output_stderr = stream.stderr.read() # 標準エラー出力の場合
      if tnum in output and target in output:
        if agilent in output:
           portnum.append(tnum)
        else:
           print("matched another device!")
           #print("You should check the connected usb-devices and /dev/tty*")
           #sys.exit()
      else:
         print("Can't find any devices!")
         print("You should check the connected usb-devices and /dev/tty*")
         sys.exit()

   agilent = 'Prolific Technology Inc.'
   port = '/dev/tty.usbserial-'
   dev_list = glob.glob("/dev/tty.usbserial-*")
   portnum = []
   if len(dev_list) < 1:
      print("Can't find any devices at /dev/tty.usbserial-**")
      print("You should check the connected usb-devices and /dev/tty*")
      sys.exit()
   for i in range(len(dev_list)):
      idx = dev_list[i].find('-')
      pnum = dev_list[i][idx+1:]
      serialnum(pnum)

   return portnum[0]

def ChangeDelay(delaytime):
    portnum = get_serial_num()
    ser = serial.Serial("/dev/tty.usbserial-{0}".format(portnum),57600,timeout=1)
    time.sleep(2)
    ser.write(b"OUTPUT OFF\n")
    ser.write(b"*IDN?\n");ser.readline()
    ser.write(b"TRIGger:DELay "+ str(delaytime).encode() +b"\n")
    time.sleep(2)
    ser.write(b"OUTPUT ON\n")
    time.sleep(2)
    ser.close()
    print("Trigger Delay time => {0}".format(delaytime))