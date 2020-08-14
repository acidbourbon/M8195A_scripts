#!/usr/bin/env python3
import SCPI_socket as sock
import struct
from time import sleep
import numpy as np
import sys
import os

from scipy import interpolate

# use Nuno's PyPi module
from PyLTSpice.LTSpice_RawRead import RawRead

def resample(target_x,data_x,data_y,**kwargs):
  fill_value = float(kwargs.get("fill_value",0.))
  f = interpolate.interp1d(data_x,data_y,bounds_error=False, fill_value=fill_value)
  out_x = target_x
  out_y = f(target_x)
  return (out_x,out_y)




def send_ltspice(**kwargs):

  my_file     = str(kwargs.get("file",""))
  signal      = str(kwargs.get("signal",""))

  trace       = int(kwargs.get("trace",1))
  #on_val      = float(kwargs.get("on_val",0.5))
  idle_val    = float(kwargs.get("idle_val",0))
  yscale      = float(kwargs.get("yscale",1))
  xscale      = float(kwargs.get("xscale",1))
  #width       = float(kwargs.get("width",50e-9))
  delay       = float(kwargs.get("delay",0e-9))
  #offset      = float(kwargs.get("offset",0e-9))
  sample_rate = int(float(kwargs.get("sample_rate",65e9)))
  invert      = int(kwargs.get("invert",0))
  ip          = str(kwargs.get("ip","192.168.0.203"))


  signal1     = str(kwargs.get("signal1",""))
  signal2     = str(kwargs.get("signal2",""))
  signal3     = str(kwargs.get("signal3",""))
  signal4     = str(kwargs.get("signal4",""))

  multichan = 0
  multichan_dic = {}

  if ((signal != "") and (trace <= 4) and (trace >=1)):
    multichan_dic[trace] = signal

  if (signal1 != ""):
    multichan = 1
    multichan_dic[1] = signal1 

  if (signal2 != ""):
    multichan = 1
    multichan_dic[2] = signal2 

  if (signal3 != ""):
    multichan = 1
    multichan_dic[3] = signal3 

  if (signal4 != ""):
    multichan = 1
    multichan_dic[4] = signal4 

  if (len(multichan_dic.keys()) == 0):
    print("I got no signal= argument. Stop.")
    exit()

  #print(multichan_dic)
  #exit()


  if ((sample_rate < 53.76e9) or (sample_rate > 65e9)):
    print('sample rate must be >=53.76e9 and <= 65.0e9')
    exit()

  
  if (my_file == ""):
    print("no file=<file> argument given")
    exit()

  if (os.path.exists(my_file) == False):
    raise NameError("file {} does not exist!".format(my_file))
    exit()


  ltr = RawRead(my_file)
    
                                                                  
  IR1 = ltr.get_trace(signal)
  x = ltr.get_trace("time") 
                                                                        
  #  #### the abs() is a quick and dirty fix for some strange sign decoding errors
  xdata = abs(x.get_wave(0))
  ydata = IR1.get_wave(0)


  xdata = xdata*xscale + delay

  width = xdata[-1]

  ydata = ydata*yscale


  target_x = np.arange(0,width,1./sample_rate)
  target_x , target_y = resample(target_x,xdata,ydata,fill_value=idle_val)

  if( np.max(np.abs(target_y)) > 0.5):
    print("####################################")
    print("## WARNING: Waveform will clip!!! ##")
    print("####################################")

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
  send_ltspice( **dict(arg.split('=') for arg in sys.argv[1:])) # kwargs
