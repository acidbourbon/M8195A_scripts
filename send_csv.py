#!/usr/bin/env python3

import M8195A as awg
from M8195A import spice_float as float

from time import sleep
import numpy as np
import sys
import os


def send_csv(**kwargs):

  delimiter   = str(kwargs.get("delimiter",","))
  
  my_file     = str(kwargs.get("file",""))

  trace       = int(kwargs.get("trace",1))
  idle_val    = float(kwargs.get("idle_val",0))
  yscale      = float(kwargs.get("yscale",1))
  xscale      = float(kwargs.get("xscale",1))
  delay       = float(kwargs.get("delay",0e-9))
  sample_rate = int(float(kwargs.get("sample_rate",65e9)))
  invert      = int(kwargs.get("invert",0))
  
  ip = "192.168.0.203"
  if(os.getenv('M8195A_IP')):
    ip = os.getenv('M8195A_IP')
  ip          = str(kwargs.get("ip",ip))
  print("target ip : {}".format(ip))
  
  period      = float(kwargs.get("period",0))


  tcol       = int(kwargs.get("tcol","0"))
  ycol       = str(kwargs.get("ycol","1"))
  ch1col     = str(kwargs.get("ch1col",""))
  ch2col     = str(kwargs.get("ch2col",""))
  ch3col     = str(kwargs.get("ch3col",""))
  ch4col     = str(kwargs.get("ch4col",""))

  watch_changes  = int(kwargs.get("watch_changes",0))
  
  
  
  
  
  

  multichan_dic = {}

  if ((ycol != "") and (trace <= 4) and (trace >=1)):
    multichan_dic[trace] = int(ycol)

  if (ch1col != ""):
    multichan_dic[1] = int(ch1col)

  if (ch2col != ""):
    multichan_dic[2] = int(ch2col)

  if (ch3col != ""):
    multichan_dic[3] = int(ch3col)

  if (ch4col != ""):
    multichan_dic[4] = int(ch4col)

  if (len(multichan_dic.keys()) == 0):
    print("I got no signal= argument. Stop.")
    exit()



  
  if (my_file == ""):
    print("no file=<file> argument given")
    exit()

  if (os.path.exists(my_file) == False):
    raise NameError("file {} does not exist!".format(my_file))
    exit()


  last_mod_date = 0

  loop_cntr = 0
  

  while(1):
    
    # get .raw file modification date
    mod_date = os.path.getmtime(my_file)

    if ( mod_date != last_mod_date):
      if (watch_changes):
        print(" ")
        print("csv input file has changed!")

      last_mod_date = mod_date

      session = awg.open_session(ip)


      print("read csv file \"{}\"".format(my_file))
      try:
        data = np.loadtxt(my_file, delimiter=delimiter)
      except:
        raise NameError("sth went wrong while reading csv file \"{}\"".format(my_file))
      finally:
        print("success!")

        
      for trace in multichan_dic.keys():
      
        ch_data_col = multichan_dic[trace]
        print("time data is in csv col {:d}".format(tcol))
        print("ch{:d} data is in csv col {:d}".format(trace,ch_data_col))
        
        xdata = data[:,tcol]*xscale
        xdata += delay
      
        ydata = data[:,ch_data_col]*yscale
        
        print("success!")
        
        awg.program_trace( xdata, ydata, 
                           trace       = trace,
                           idle_val    = idle_val,
                           xscale      = xscale,
                           yscale      = yscale,
                           delay       = delay,
                           invert      = invert,
                           sample_rate = sample_rate,
                           period      = period
                        )



      # done with individual trace stuff

      awg.run()
      awg.close_session()

      if (watch_changes == 0):
        break
      else:
        print ("--------------------------------------------------")
        print ("watching file {}, will reprogram AWG on change ...".format(my_file)) 
        print ("press CTRL+C if you want to abort")

    
    sleep(1) 
    
    # display funny scanning animation
    print(loop_cntr*"_"+"#"+(9-loop_cntr)*"_",end="\r")
    loop_cntr = (loop_cntr +1)%10
  
  






  
  





if __name__=='__main__':
  send_csv( **dict(arg.split('=') for arg in sys.argv[1:])) # kwargs
