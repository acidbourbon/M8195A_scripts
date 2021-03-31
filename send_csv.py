#!/usr/bin/env python3

from M8195A import send_csv 

import sys






if __name__=='__main__':
  send_csv( **dict(arg.split('=') for arg in sys.argv[1:])) # kwargs
