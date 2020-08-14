#!/usr/bin/env python3

import M8195A as awg
from M8195A import spice_float

import SCPI_socket as sock
from time import sleep
import numpy as np
import sys
import os


### suppress STDOUT in this try except block
old_stdout = sys.stdout
sys.stdout = open(os.devnull, "w")
try:
  # use Nuno's PyPi module
  from PyLTSpice.LTSpice_RawRead import RawRead
except:
  raise NameError("pyltspice module not found. :/\nplease install the pyltspice module via pip\n  sudo pip3 install pyltspice")
finally:
  sys.stdout.close()
  sys.stdout = old_stdout



def send_ltspice(**kwargs):

  my_file     = str(kwargs.get("file",""))
  signal      = str(kwargs.get("signal",""))

  trace       = int(kwargs.get("trace",1))
  idle_val    = spice_float(kwargs.get("idle_val",0))
  yscale      = spice_float(kwargs.get("yscale",1))
  xscale      = spice_float(kwargs.get("xscale",1))
  delay       = spice_float(kwargs.get("delay",0e-9))
  sample_rate = int(spice_float(kwargs.get("sample_rate",65e9)))
  invert      = int(kwargs.get("invert",0))
  ip          = str(kwargs.get("ip","192.168.0.203"))


  signal1     = str(kwargs.get("signal1",""))
  signal2     = str(kwargs.get("signal2",""))
  signal3     = str(kwargs.get("signal3",""))
  signal4     = str(kwargs.get("signal4",""))

  watch_changes  = int(kwargs.get("watch_changes",0))

  multichan_dic = {}

  if ((signal != "") and (trace <= 4) and (trace >=1)):
    multichan_dic[trace] = signal

  if (signal1 != ""):
    multichan_dic[1] = signal1 

  if (signal2 != ""):
    multichan_dic[2] = signal2 

  if (signal3 != ""):
    multichan_dic[3] = signal3 

  if (signal4 != ""):
    multichan_dic[4] = signal4 

  if (len(multichan_dic.keys()) == 0):
    print("I got no signal= argument. Stop.")
    exit()


  if ((sample_rate < 53.76e9) or (sample_rate > 65e9)):
    print('sample rate must be >=53.76e9 and <= 65.0e9')
    exit()

  
  if (my_file == ""):
    print("no file=<file> argument given")
    exit()

  if (os.path.exists(my_file) == False):
    raise NameError("file {} does not exist!".format(my_file))
    exit()


  last_mod_date = 0
  # get raw file modification date

  loop_cntr = 0
  while(1):
    mod_date = os.path.getmtime(my_file)

    if ( mod_date != last_mod_date):
      if (watch_changes):
        print(" ")
        print("LTSpice output has changed!")

      last_mod_date = mod_date

      session = awg.open_session(ip)

      awg.set_sample_rate(sample_rate)

      ltr = RawRead(my_file)
        
      for trace in multichan_dic.keys():
      
        signal = multichan_dic[trace]
        
        print("read LTSpice signal \"{}\"...".format(signal))
        
        
        ### suppress STDOUT in this try except block
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        try:
          IR1 = ltr.get_trace(signal)
          x = ltr.get_trace("time") 
                                                                                
          #  #### the abs() is a quick and dirty fix for some strange sign decoding errors
          xdata = abs(x.get_wave(0))
          ydata = IR1.get_wave(0)
        except:
          raise NameError("sth went wrong ... apparently I can't find signal \"{}\" in binary file \"{}\"".format(signal,my_file))
        finally:
          sys.stdout.close()
          sys.stdout = old_stdout
          
       
        print("success!")
        
        awg.program_trace( xdata, ydata, 
                           trace       = trace,
                           idle_val    = idle_val,
                           xscale      = xscale,
                           yscale      = yscale,
                           delay       = delay,
                           invert      = invert,
                           sample_rate = sample_rate,
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
  send_ltspice( **dict(arg.split('=') for arg in sys.argv[1:])) # kwargs
