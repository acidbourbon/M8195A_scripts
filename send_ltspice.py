#!/usr/bin/env python3

from M8195A import send_ltspice

import sys






if __name__=='__main__':
  send_ltspice( **dict(arg.split('=') for arg in sys.argv[1:])) # kwargs
