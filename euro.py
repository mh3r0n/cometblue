#!/usr/bin/python

import pexpect
import sys

class Gatt:
  def try_until(self, func, max_tries = 30, sleep_time = 1):
    from time import sleep
    for _ in range(0, max_tries):
      try:
        r = func()
        return r
      except:
        sleep(sleep_time)
    return func()

  def __init__(self, mac, debug = True):
    self.try_until(lambda: self.private__init__(mac, debug))

  def read(self, hnd):
    return self.try_until(lambda: self.private_read(hnd))

  def write(self, hnd, value):
    self.try_until(lambda: self.private_write(hnd, value))

  gatt = None
  def private__init__(self, mac, debug):
    self.gatt = pexpect.spawn('gatttool -I')

    if debug:
      self.gatt.logfile = sys.stdout
    try:
      self.gatt.sendline("connect %s" % mac),
      self.gatt.expect("Connection successful", timeout = 30)
    except pexpect.TIMEOUT:
      raise Exception("Timeout");
    except:
      raise Exception(self.parseError(self.gatt.before))

  def __del__(self):
    self.gatt.sendline("quit")

  def parseError(self, error):
    return error.split("\n")[-2] # last line is prompt

  def private_read(self, hnd):
    try:
      self.gatt.sendline("char-read-hnd 0x%x" % hnd),
      self.gatt.expect("Characteristic value/descriptor: ([0-9a-f][0-9a-f] )*[0-9a-f][0-9a-f]", timeout = 30)
    except pexpect.TIMEOUT:
      raise Exception("Timeout");
    except:
      raise Exception(self.parseError(self.gatt.before))

    s = self.gatt.after[33:]
    l = [int(x, 16) for x in s.split()]
    return l

  def private_write(self, hnd, value):
    try:
      s = "".join(["%02x" % i for i in value])
      self.gatt.sendline("char-write-req 0x%x %s" % (hnd, s)),
      self.gatt.expect("Characteristic value was written successfully", timeout = 30)
    except pexpect.TIMEOUT:
      raise Exception("Timeout");
    except:
      raise Exception(self.parseError(self.gatt.before))

class CometBlue(Gatt):
  def __init__(self, mac, pin = 0):
    Gatt.__init__(self, mac)
    assert self.getVersion() == "0.0.6-sygonix1"
    self.setPin(pin) # first setPin is for login

  def getVersion(self):
    a = self.read(0x18)
    return "".join([chr(i) for i in a])

  def getCurrentTemperature(self):
    return self.read(0x3f)[0] / 2.0

  def getPreferredTemperature(self):
    return self.read(0x3f)[1] / 2.0

  def setPin(self, pin):
    a = [pin >> i & 0xff for i in (0,8,16,24)]
    return self.write(0x47, a)

  def setPreferredTemperature(self, t):
    return self.write(0x3f, [0x80, 0x80, int(t * 2), int(t * 2), 0x00, 0x80, 0x80])

if __name__ == "__main__":
  a = {
    "Sypialnia": ["E0:E5:CF:E7:10:8D", 0000],
    "Salon":     ["E0:E5:CF:E7:10:BB", 0000],
    "Dzieciecy": ["E0:E5:CF:B0:58:48", 0000]
  }

#  blue = CometBlue(*a["Dzieciecy"])
#  blue.setPreferredTemperature(22.0)
