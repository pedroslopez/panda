#!/usr/bin/env python
import sys
import struct
import argparse
from panda import Panda
import time

class CanHandle(object):
  def __init__(self, p):
    self.p = p

  def transact(self, dat):
    print "W:",dat.encode("hex")
    self.p.isotp_send(1, dat, 0, recvaddr=2)
    ret = self.p.isotp_recv(2, 0, sendaddr=1)
    print "R:",ret.encode("hex")
    return ret

  def controlWrite(self, request_type, request, value, index, data, timeout=0):
    # ignore data in reply, panda doesn't use it
    return self.controlRead(request_type, request, value, index, 0, timeout)

  def controlRead(self, request_type, request, value, index, length, timeout=0):
    dat = struct.pack("HHBBHHH", 0, 0, request_type, request, value, index, length)
    return self.transact(dat)

  def bulkWrite(self, endpoint, data, timeout=0):
    if len(data) > 0x10:
      raise ValueError("Data must not be longer than 0x10")
    dat = struct.pack("HH", endpoint, len(data))+data
    return self.transact(dat)

  def bulkRead(self, endpoint, length, timeout=0):
    dat = struct.pack("HH", endpoint, 0)
    return self.transact(dat)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Flash pedal over can')
  parser.add_argument('--recover', action='store_true')
  parser.add_argument("fn", type=str, nargs='?', help="flash file")
  args = parser.parse_args()

  p = Panda()
  p.set_safety_mode(0x1337)

  while 1:
    if len(p.can_recv()) == 0:
      break

  if args.recover:
    p.can_send(0x200, "\xce\xfa\xad\xde\x1e\x0b\xb0\x02", 0)
    exit(0)
  else:
    p.can_send(0x200, "\xce\xfa\xad\xde\x1e\x0b\xb0\x0a", 0)

  if args.fn:
    print "flashing", args.fn
    code = open(args.fn).read()
    Panda.flash_static(CanHandle(p), code)


