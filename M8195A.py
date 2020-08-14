#!/usr/bin/env python3


import SCPI_socket as sock



import struct
from time import sleep
import numpy as np
import sys
import os
import datetime

from scipy import interpolate

local_objects = {}


def resample(target_x,data_x,data_y,**kwargs):
  fill_value = float(kwargs.get("fill_value",0.))
  f = interpolate.interp1d(data_x,data_y,bounds_error=False, fill_value=fill_value)
  out_x = target_x
  out_y = f(target_x)
  return (out_x,out_y)


def open_session(ip):
  
  # Open socket, create waveform, send data, read back and close socket
  print("connect to device ...")
  session = sock.SCPI_sock_connect(ip)
  print("*IDN?")
  idn_str = sock.SCPI_sock_query(session,"*idn?")
  print(idn_str)
  if ( "Keysight Technologies,M8195A" in idn_str):
    print("success!")
  else:
    sock.SCPI_sock_close(session)
    raise NameError("could not communicate with device, or not a Keysight Technologies,M8195A")
  local_objects["session"] = session
  return session
  


def close_session():
  print("close socket")
  sock.SCPI_sock_close(local_objects["session"])
  
  
