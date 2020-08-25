#!/usr/bin/env python3

import M8195A as awg
from M8195A import spice_float as float

import numpy as np
import sys
import os


def pulser(**kwargs):

  trace       = int(kwargs.get("trace",1))
  on_val      = float(kwargs.get("on_val",0.5))
  idle_val    = float(kwargs.get("idle_val",0))
  width       = float(kwargs.get("width",50e-9))
  delay       = float(kwargs.get("delay",0e-9))
  sample_rate = int(float(kwargs.get("sample_rate",65e9)))
  invert      = int(kwargs.get("invert",0))
  ip          = str(kwargs.get("ip","192.168.0.203"))
  period      = float(kwargs.get("period",0))
  yscale      = float(kwargs.get("yscale",1))
  xscale      = float(kwargs.get("xscale",1))
  
  leading_edge   = float(kwargs.get("leading_edge",0))
  trailing_edge  = float(kwargs.get("trailing_edge",0))

  
  
  #xdata = np.arange(0,width,1./sample_rate)
  #ydata = np.ones(len(xdata))*on_val
  
  delay += leading_edge/2
  
  xlist = []
  ylist = []
  
  xlist += [-leading_edge/2]
  ylist += [idle_val]
  
  xlist += [leading_edge/2]
  ylist += [on_val]
  
  xlist += [width - trailing_edge/2]
  ylist += [on_val]
  
  xlist += [width + trailing_edge/2]
  ylist += [idle_val]
  
  
  xdata = np.array(xlist)
  ydata = np.array(ylist)
  
  session = awg.open_session(ip)

  
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

  awg.run()
  awg.close_session()




if __name__=='__main__':
  pulser( **dict(arg.split('=') for arg in sys.argv[1:])) # kwargs
