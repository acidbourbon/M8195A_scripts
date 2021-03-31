#!/usr/bin/env python3


import sys
import os

from M8195A import pulser






if __name__=='__main__':
  pulser( **dict(arg.split('=') for arg in sys.argv[1:])) # kwargs
