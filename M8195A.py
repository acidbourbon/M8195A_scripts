#!/usr/bin/env python3


#import SCPI_socket as sock



import struct
from time import sleep
import numpy as np
import sys
import os
import datetime

from scipy import interpolate

local_objects = {}





def send_data(xdata,ydata,**kwargs):

  trace       = int(kwargs.get("trace",1))
  idle_val    = spice_float(kwargs.get("idle_val",0))
  delay       = spice_float(kwargs.get("delay",0e-9))
  sample_rate = int(spice_float(kwargs.get("sample_rate",65e9)))
  invert      = int(kwargs.get("invert",0))
  
  ip = "192.168.0.203"
  if(os.getenv('M8195A_IP')):
    ip = os.getenv('M8195A_IP')
  ip          = str(kwargs.get("ip",ip))
  print("target ip : {}".format(ip))
  
  period      = spice_float(kwargs.get("period",0))
  yscale      = spice_float(kwargs.get("yscale",1))
  xscale      = spice_float(kwargs.get("xscale",1))
  

  
  
  
  
  my_xdata = np.array(xdata)
  my_ydata = np.array(ydata)
  
  session = open_session(ip)

  
  program_trace( my_xdata, my_ydata, 
                     trace       = trace,
                     idle_val    = idle_val,
                     xscale      = xscale,
                     yscale      = yscale,
                     delay       = delay,
                     invert      = invert,
                     sample_rate = sample_rate,
                     period      = period
                  )

  run()
  close_session()



def pulser(**kwargs):

  trace       = int(kwargs.get("trace",1))
  on_val      = spice_float(kwargs.get("on_val",0.5))
  idle_val    = spice_float(kwargs.get("idle_val",0))
  width       = spice_float(kwargs.get("width",50e-9))
  delay       = spice_float(kwargs.get("delay",0e-9))
  sample_rate = int(spice_float(kwargs.get("sample_rate",65e9)))
  invert      = int(kwargs.get("invert",0))
  
  ip = "192.168.0.203"
  if(os.getenv('M8195A_IP')):
    ip = os.getenv('M8195A_IP')
  ip          = str(kwargs.get("ip",ip))
  print("target ip : {}".format(ip))
  
  period      = spice_float(kwargs.get("period",0))
  yscale      = spice_float(kwargs.get("yscale",1))
  xscale      = spice_float(kwargs.get("xscale",1))
  
  leading_edge   = spice_float(kwargs.get("leading_edge",0))
  trailing_edge  = spice_float(kwargs.get("trailing_edge",0))

  
  
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
  
  session = open_session(ip)

  
  program_trace( xdata, ydata, 
                     trace       = trace,
                     idle_val    = idle_val,
                     xscale      = xscale,
                     yscale      = yscale,
                     delay       = delay,
                     invert      = invert,
                     sample_rate = sample_rate,
                     period      = period
                  )

  run()
  close_session()





def send_csv(**kwargs):

  delimiter   = str(kwargs.get("delimiter",","))
  
  my_file     = str(kwargs.get("file",""))

  trace       = int(kwargs.get("trace",1))
  idle_val    = spice_float(kwargs.get("idle_val",0))
  yscale      = spice_float(kwargs.get("yscale",1))
  xscale      = spice_float(kwargs.get("xscale",1))
  delay       = spice_float(kwargs.get("delay",0e-9))
  sample_rate = int(spice_float(kwargs.get("sample_rate",65e9)))
  invert      = int(kwargs.get("invert",0))
  
  ip = "192.168.0.203"
  if(os.getenv('M8195A_IP')):
    ip = os.getenv('M8195A_IP')
  ip          = str(kwargs.get("ip",ip))
  print("target ip : {}".format(ip))
  
  period      = spice_float(kwargs.get("period",0))


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

      session = open_session(ip)


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
        
        program_trace( xdata, ydata, 
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

      run()
      close_session()

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
  
  




def send_ltspice(**kwargs):
  
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
  ### end of STDOUT suppression



  my_file     = str(kwargs.get("file",""))
  signal      = str(kwargs.get("signal",""))

  trace       = int(kwargs.get("trace",1))
  idle_val    = spice_float(kwargs.get("idle_val",0))
  yscale      = spice_float(kwargs.get("yscale",1))
  xscale      = spice_float(kwargs.get("xscale",1))
  delay       = spice_float(kwargs.get("delay",0e-9))
  sample_rate = int(spice_float(kwargs.get("sample_rate",65e9)))
  invert      = int(kwargs.get("invert",0))
  
  ip = "192.168.0.203"
  if(os.getenv('M8195A_IP')):
    ip = os.getenv('M8195A_IP')
  ip          = str(kwargs.get("ip",ip))
  print("target ip : {}".format(ip))
  
  period      = spice_float(kwargs.get("period",0))


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
        print("LTSpice output has changed!")

      last_mod_date = mod_date

      session = open_session(ip)

      print("read LTSpice binary file \"{}\"".format(my_file))
      try:
        ltr = RawRead(my_file)
      except:
        raise NameError("sth went wrong while reading LTSpice binary file \"{}\"".format(my_file))
      finally:
        print("success!")
        
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
        
        program_trace( xdata, ydata, 
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

      run()
      close_session()

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
  session = SCPI_sock_connect(ip)
  print("*IDN?")
  idn_str = SCPI_sock_query(session,"*idn?")
  print(idn_str)
  if ( "Keysight Technologies,M8195A" in idn_str):
    print("success!")
  else:
    SCPI_sock_close(session)
    raise NameError("could not communicate with device, or not a Keysight Technologies,M8195A")
  local_objects["session"] = session
  return session
  


def close_session():
  if (not("session" in local_objects.keys())):
    raise NameError("there is no running communication session with AWG!")
  session = local_objects["session"]
  
  print("close socket")
  SCPI_sock_close(session)
  
  
def run():
  if (not("session" in local_objects.keys())):
    raise NameError("there is no running communication session with AWG!")
  session = local_objects["session"]
 
  print("RUN!")
  SCPI_sock_send(session,":INIT:IMM")
  
  
def stop():
  if (not("session" in local_objects.keys())):
    raise NameError("there is no running communication session with AWG!")
  session = local_objects["session"]
 
  print("STOP!")
  SCPI_sock_send(session,":ABOR")
  
 
def set_sample_rate(sample_rate):
  if (not("session" in local_objects.keys())):
    raise NameError("there is no running communication session with AWG!")
  session = local_objects["session"]
  
  if ((sample_rate < 53.76e9) or (sample_rate > 65e9)):
    raise NameError('sample rate must be >=53.76e9 and <= 65.0e9')
  
  print("attempting to set sample rate : {:f} Hz".format(sample_rate))
  
  SCPI_sock_send(session,":INIT:IMM")
  SCPI_sock_send(session,":SOUR:FREQ:RAST {:d}".format(int(sample_rate)))
  #print("read back sample rate (Hz):")
  read_back = SCPI_sock_query(session,":SOUR:FREQ:RAST?")
  SCPI_sock_send(session,":ABOR")
  #print(read_back)
  if( float(read_back) == float(sample_rate)):
    print("success!")
  else:
    raise NameError("could not set desired sample rate!")
  

def next_int_mult_128(n):
  return np.max([int((n)/128+1)*128,128]) # multiples of 128


def prev_int_mult_128(n):
  return np.max([int((n)/128)*128,128]) # multiples of 128

  
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
    #mem_size = next_int_mult_128(int(period * sample_rate))
    #mem_size = np.min([mem_size,MAX_MEM_SIZE])
    
    print("NOTE: overriding sample rate to match desired period!")
    
    sample_rate = 65e9

    mem_size = prev_int_mult_128(int(period * sample_rate))
    mem_size = np.min([mem_size,MAX_MEM_SIZE])
    hypothetical_period = 1/sample_rate*mem_size
    rate_scaler = hypothetical_period/period
    
    sample_rate *= rate_scaler
    sample_rate = int(sample_rate)
    
    
  set_sample_rate(sample_rate)
  
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
  # +-100 mV is the smallest DAC range
  if (volt < 0.1):
    volt = 0.1
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
  sample_len = next_int_mult_128(n)
  sample_len = np.min([sample_len,mem_size])
  #print("sample len :{:d}".format(sample_len))
  
  #dataList = [-100 for i in range(sample_len)]
  
  dataList = idle_val_dac*np.ones(sample_len)
  
  n_ = np.min([n,sample_len])
  
  dataList[0:n_] = target_y[0:n_]
  dataList = dataList.astype(np.int).tolist()
  
  dataString = ",".join(map(str,dataList))
  cmdString = ":TRAC{:d}:DATA 1,{:d},{}".format(trace,n_offset,dataString)
  
  
  
  #print(SCPI_sock_query(session,":TRAC{:d}:CAT?".format(trace)))
  SCPI_sock_send(session,":TRAC{:d}:DEL:ALL".format(trace))
  SCPI_sock_send(session,":TRAC{:d}:DEF 1,{:d},{:d}".format(trace,mem_size,idle_val_dac))
  
  #delete all traces with wrong mem_size
  for i in range(1,5):
    cat_answer = SCPI_sock_query(session,":TRAC{:d}:CAT?".format(i))
    cat_answer.replace("\n","")
    cat_answer.replace("\r","")
    cat_answer.replace(" ","")
    #print(cat_answer)
    if( (cat_answer != "1,{:d}".format(mem_size))  and (cat_answer != "0,0" )): 
      print("delete trace {:d}, because wrong mem size / wrong period".format(i))
      SCPI_sock_send(session,":TRAC{:d}:DEL:ALL".format(i))
  
  
  #send data
  print("sending data ...")
  SCPI_sock_send(session,cmdString)
  #print(SCPI_sock_query(session,":TRAC1:DATA? 1,0,512"))

  print("set output voltage ...")
  SCPI_sock_send(session,":VOLT{:d} {:3.3f}".format(trace,volt))

  print("Output {:d} on ...".format(trace))
  SCPI_sock_send(session,":OUTP{:d} ON".format(trace))
  
  
  
  
  
##################################################
##                 SCPI_socket                  ##
##################################################


# Python SCPI socket functions
# This is not an official Keysight driver.  
# Very limited testing has been done.
# Feel free to modify this
# Version 0.5 


import socket

def SCPI_sock_connect(ipaddress,port=5025):
    """ Opens up a socket connection between an instrument and your PC
        Returns the socket session

        Arguments:
        ipaddress -> ip address of the instrument
        port -> optional -> socket port of the instrument (default 5025)"""

    try:
        session=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #session.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 0)
        #session.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, 0)
        session.connect((ipaddress,port))
    except IOError:
        print( "Failed to connect to the instrument, pleace check your IP address" )
        return
    return session

def SCPI_sock_send(session,command,error_check=False):
    #print("SCPI send: {}".format(command))
    """Sends a command to an instrument

        Arguments:
        session -> TCPIP socket connection
        command -> text containing an instrument command
        error_check -> optional -> Check for instrument errors (default False)"""
    
    resp = " "
    session.sendall(str.encode(command + "\n"))

    if error_check==True:
        err = get_error(session, command)        
        
def SCPI_sock_query(session,command,error_check=False):
    """Sends a query to an instrument
        Returns the query response
        
        Arguments:
        session -> TCPIP socket connection
        command -> text containing an instrument command
        error_check -> optional -> Check for instrument errors (default False)"""
    
    session.settimeout(4.0)
    try:
        session.sendall(str.encode(command + "\n"))
        response = getDataFromSocket(session)
        if error_check==True:
            err = get_error(session, command)
            if err:
                response = "<ERROR>"
        return response
        
    except socket.timeout:
        print( "Query error:" )
        get_error(session, command)
        response = "<ERROR>"
        return response

def SCPI_sock_close(session):
    """Closes the socket connection

        Argument:
        session -> TCPIP socket connection"""
    
    session.close()

def getDataFromSocket(session):
    """Reads from a socket until a newline is read
        Returns the data read

        Argument:
        session -> TCPIP socket"""
    
    dat = ""
    while 1:
        message = session.recv(4096).decode()
        last=len(message)
        if message[last-1] == "\n":
            dat=dat+message[:-1]
            return dat
        else:
            dat=dat+message

def get_error(session, command):
    """Checks an instrument for errors and print( them out )
        Returns True if any errors are encountered

        Arguments:
        session -> TCPIP socket connection
        command -> text containing an instrument command"""
        
    has_err=False
    resp = SCPI_sock_query(session,"SYST:ERR?")
    
    if int(resp[:2]) != 0:
        print( "Your command: " + command + " has errors:" )
        print( resp )
        has_err = True
    while int(resp[:2]) != 0:
        resp=SCPI_sock_query(session,"SYST:ERR?")
        if int(resp[:2]) != 0:
            print( resp )

    return has_err



  
  
