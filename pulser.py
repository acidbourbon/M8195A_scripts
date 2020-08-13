#!/usr/bin/env python3
import SCPI_socket as sock
import struct
from time import sleep
import numpy as np
import sys



def pulser(**kwargs):

  trace       = int(kwargs.get("trace",1))
  on_val      = float(kwargs.get("on_val",0.5))
  idle_val    = float(kwargs.get("idle_val",0))
  width       = float(kwargs.get("width",50e-9))
  delay       = float(kwargs.get("delay",0e-9))
  #offset      = float(kwargs.get("offset",0e-9))
  sample_rate = int(float(kwargs.get("sample_rate",65e9)))
  invert      = int(kwargs.get("invert",0))
  ip          = str(kwargs.get("ip","192.168.0.203"))

  if ((sample_rate < 53.76e9) or (sample_rate > 65e9)):
    raise NameError('sample rate must be >=53.76e9 and <= 65.0e9')

  #volt        = float(kwargs.get("volt",0.5))
  offset = 0
  volt = np.max(np.abs([idle_val,on_val]))
  idle_val = idle_val/volt
  on_val   = on_val/volt
  volt = volt*2

  if(invert):
    idle_val = -idle_val
    on_val   = - on_val

  idle_val_dac = int(idle_val*127)
  on_val_dac = int(on_val*127)

  n_delay = int(delay*sample_rate) 
  n_offset = int(offset*sample_rate) 
  n = int(width*sample_rate)
  
  # sample len must be a multiple of 128
  sample_len = np.max([int((n+n_delay)/128+1)*128,128]) # multiples of 128
  #print("sample len :{:d}".format(sample_len))
  
  #dataList = [-100 for i in range(sample_len)]
  
  dataList = idle_val_dac*np.ones(sample_len)
  
  dataList[0+n_delay:n+n_delay] = on_val_dac*np.ones(n)
  dataList = dataList.astype(np.int).tolist()
  
  dataString = ",".join(map(str,dataList))
  cmdString = ":TRAC{:d}:DATA 1,{:d},{}".format(trace,n_offset,dataString)
  
  # Open socket, create waveform, send data, read back and close socket
  session = sock.SCPI_sock_connect(ip)

  print(sock.SCPI_sock_query(session,"*idn?"))

  sock.SCPI_sock_send(session,":INIT:IMM")
  print("sample rate (Hz):")
  sock.SCPI_sock_send(session,":SOUR:FREQ:RAST {:d}".format(int(sample_rate)))
  print(sock.SCPI_sock_query(session,":SOUR:FREQ:RAST?"))
  
  sock.SCPI_sock_send(session,":ABOR")
  
  print(sock.SCPI_sock_query(session,":TRAC{:d}:CAT?".format(trace)))
  sock.SCPI_sock_send(session,":TRAC{:d}:DEL:ALL".format(trace))
  sock.SCPI_sock_send(session,":TRAC{:d}:DEF 1,262144,{:d}".format(trace,idle_val_dac))
  
  #send data
  print("sending data ...")
  sock.SCPI_sock_send(session,cmdString)
  #print(sock.SCPI_sock_query(session,":TRAC1:DATA? 1,0,512"))

  print("set output voltage ...")
  sock.SCPI_sock_send(session,":VOLT{:d} {:3.3f}".format(trace,volt))

  print("Output {:d} on ...".format(trace))
  sock.SCPI_sock_send(session,":OUTP{:d} ON".format(trace))
  print("run!")
  sock.SCPI_sock_send(session,":INIT:IMM")
  print("close socket")
  sock.SCPI_sock_close(session)
  
  





if __name__=='__main__':
  pulser( **dict(arg.split('=') for arg in sys.argv[1:])) # kwargs
