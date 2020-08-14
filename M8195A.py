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


def spice_float(argument):
   
  if( isinstance(argument,str)):
   
    expr = argument
    if("p" in expr):
      expr = expr.replace("p","e-12")
    elif("n" in expr):
      expr = expr.replace("n","e-9")
    elif("u" in expr):
      expr = expr.replace("u","e-6")
    elif("m" in expr):
      expr = expr.replace("m","e-3")
    elif("k" in expr):
      expr = expr.replace("k","e3")
    elif("Meg" in expr):
      expr = expr.replace("Meg","e6")
    elif("M" in expr):
      expr = expr.replace("M","e6")
    elif("G" in expr):
      expr = expr.replace("G","e9")
    elif("T" in expr):
      expr = expr.replace("T","e12")
      
    try:
      number = float(expr)
    except:
      raise NameError("cannot convert \"{}\" to a reasonable number".format(argument))
  else:
    number = float(argument)
  
  return number




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
  if (not("session" in local_objects.keys())):
    raise NameError("there is no running communication session with AWG!")
  session = local_objects["session"]
  
  print("close socket")
  sock.SCPI_sock_close(session)
  
  
def run():
  if (not("session" in local_objects.keys())):
    raise NameError("there is no running communication session with AWG!")
  session = local_objects["session"]
 
  print("RUN!")
  sock.SCPI_sock_send(session,":INIT:IMM")
  
  
def stop():
  if (not("session" in local_objects.keys())):
    raise NameError("there is no running communication session with AWG!")
  session = local_objects["session"]
 
  print("STOP!")
  sock.SCPI_sock_send(session,":ABOR")
  
 
def set_sample_rate(sample_rate):
  if (not("session" in local_objects.keys())):
    raise NameError("there is no running communication session with AWG!")
  session = local_objects["session"]
  
  print("attempting to set sample rate : {:f} Hz".format(sample_rate))
  
  sock.SCPI_sock_send(session,":INIT:IMM")
  sock.SCPI_sock_send(session,":SOUR:FREQ:RAST {:d}".format(int(sample_rate)))
  #print("read back sample rate (Hz):")
  read_back = sock.SCPI_sock_query(session,":SOUR:FREQ:RAST?")
  sock.SCPI_sock_send(session,":ABOR")
  #print(read_back)
  if( float(read_back) == float(sample_rate)):
    print("success!")
  else:
    raise NameError("could not set desired sample rate!")
  
  
  
def program_trace(xdata,ydata,**kwargs):
  if (not("session" in local_objects.keys())):
    raise NameError("there is no running communication session with AWG!")
  session = local_objects["session"]
  
  
  MAX_MEM_SIZE = 262144
  
  mem_size     = MAX_MEM_SIZE
  
  trace       = int(kwargs.get("trace",1))
  idle_val    = float(kwargs.get("idle_val",0))
  yscale      = float(kwargs.get("yscale",1))
  xscale      = float(kwargs.get("xscale",1))
  delay       = float(kwargs.get("delay",0e-9))
  sample_rate = int(float(kwargs.get("sample_rate",65e9)))
  invert      = int(kwargs.get("invert",0))
  period      = float(kwargs.get("period",0))
  
  if(period != 0):
    mem_size = int(period * sample_rate)
    mem_size = np.min([mem_size,MAX_MEM_SIZE])
  
  print("preparing data for channel {:d}".format(trace))
  
  
  xdata = xdata*xscale + delay

  width = xdata[-1]

  ydata = ydata*yscale


  target_x = np.arange(0,width,1./sample_rate)
  target_x , target_y = resample(target_x,xdata,ydata,fill_value=idle_val)
  

  if( np.max(np.abs(target_y)) > 0.5):
    print("############################################")
    print("## WARNING: Waveform on ch {:d} will clip!!! ##".format(trace))
    print("############################################")

  # clip to allowed value range
  target_y[target_y > 0.5] = 0.5
  target_y[target_y < -0.5] = -0.5


  #volt        = float(kwargs.get("volt",0.5))
  offset = 0
  volt = np.max(np.abs(target_y))
  idle_val = idle_val/volt
  target_y = target_y*127./volt
  volt = volt*2

  if(invert):
    idle_val = -idle_val
    target_y = -target_y


  idle_val_dac = int(idle_val*127)

  #n_delay = int(delay*sample_rate) 
  n_offset = int(offset*sample_rate) 
  n = int(len(target_x))
  
  # sample len must be a multiple of 128
  sample_len = np.max([int((n)/128+1)*128,128]) # multiples of 128
  #print("sample len :{:d}".format(sample_len))
  
  #dataList = [-100 for i in range(sample_len)]
  
  dataList = idle_val_dac*np.ones(sample_len)
  
  dataList[0:n] = target_y
  dataList = dataList.astype(np.int).tolist()
  
  dataString = ",".join(map(str,dataList))
  cmdString = ":TRAC{:d}:DATA 1,{:d},{}".format(trace,n_offset,dataString)
  
  
  #print(sock.SCPI_sock_query(session,":TRAC{:d}:CAT?".format(trace)))
  sock.SCPI_sock_send(session,":TRAC{:d}:DEL:ALL".format(trace))
  sock.SCPI_sock_send(session,":TRAC{:d}:DEF 1,{:d},{:d}".format(trace,mem_size,idle_val_dac))
  
  #send data
  print("sending data ...")
  sock.SCPI_sock_send(session,cmdString)
  #print(sock.SCPI_sock_query(session,":TRAC1:DATA? 1,0,512"))

  print("set output voltage ...")
  sock.SCPI_sock_send(session,":VOLT{:d} {:3.3f}".format(trace,volt))

  print("Output {:d} on ...".format(trace))
  sock.SCPI_sock_send(session,":OUTP{:d} ON".format(trace))
  
  
