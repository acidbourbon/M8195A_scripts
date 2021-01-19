# M8195A_scripts

## Dependencies
- python3
- numpy
- scipy
- pyltspice

```
# install all dependencies

sudo pip3 install numpy scipy pyltspice
```

## Prerequisites

### The server on the windows machine

The Keysight M8195 consists of two parts: The hardware and the "Soft Front Panel" software.
This collection of scripts talks DOES NOT talk to the hardware directly (because the hardware is dumb),
but to the "Soft Front Panel", which provides the SCPI interface to the instrument as a whole.

"Soft Front Panel" must run on a Windows machine with its port number 2025 exposed to the network.

The SCPI interface IS NOT running by default. "Soft Front Panel" needs to be started with command line
argument "/Socket 2025" in order for our scripts to work.

This is easily facilitated by creating a Desktop shortcut to the software and editing it, as shown below:

![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/soft_front_panel_arguments.png)

Then start the software via this shortcut.
Congratulations, you now have a server running, that grants Linux and Windows machines in this network
access to the M8295A signal generator.

***

### The clients on either Windows or Linux

The below scripts have been written and tested on a Linux machine which is in the same
network as the Windows machine running the "Soft Front Panel" software.
The scripts have also been proven to work on a windows machine with the IDLE Python3 release for Windows.

For the scripts to properly communicate with the server they need to be called with with the "ip" argument.
The given ip is the ip of the windows server running "Soft Front Panel":
```
./pulser.py       ip=192.168.0.123 <further arguments>
./send_csv.py     ip=192.168.0.123 <further arguments>
./send_ltspice.py ip=192.168.0.123 <further arguments>
```
If you don't want to type the ip argument all the time, you can export the ip as an environment variable once:
```
export M8195A_ip=192.168.0.123
```


LTSpice, a Windows application,
runs perfectly fine on Linux via WINE. 
(http://ltspice.analog.com/software/LTspiceXVII.exe)

***


## pulser.py

- generate square pulses with arbitrary "idle" and "on" levels (-0.5 to 0.5V)


example usage:

![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/pulser.png)

```
./pulser.py width=50e-9 trace=1 on_val=0.5 idle_val=0
./pulser.py width=30n trace=2 on_val=-300m idle_val=100m delay=10n

```


![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/pulser2.png)

```
./pulser.py trace=2 width=10n leading_edge=2n trailing_edge=10n delay=5n on_val=500m
./pulser.py trace=3 width=10n leading_edge=2.5n trailing_edge=1n delay=15n on_val=-400m
```

![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/pulser_period.png)

```
./pulser.py trace=1 width=10n period=50n
```
- if no "period=" argument is given, the AWG will use its maximum memory depth, resulting
in the maximum sample length of circa 4us (at maximum sampling rate = 65GHz).

optional parameters/standard values:
```
sample_rate=65e9
period=0
invert=0
on_val=0.5
idle_val=0
trace=1
width=50n
delay=0n
ip=192.168.0.203
xscale=1
yscale=1
```

- if leading and trailing edge are set to macroscopic values, the width is defined between the 50% points
- time and voltage definitions can be given with numeric postfixes, i.e. n=1e-9 p=1e-12 m=1e-3, etc ...

## send_csv.py

- read in two column csv file and send it to the AWG
- first column is time in seconds
- second column is voltage in volts
- standard delimiter is "," but can be adjusted (see below)
- waveform is resampled/interpolated, so time steps can be arbitrary


example usage:

![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/send_csv.png)

```
./send_csv.py file=waveform.csv trace=1 
./send_csv.py file=waveform.csv trace=2 delay=10n invert=1 yscale=0.5 xscale=0.3

```

![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/csv_period.png)
```
./send_csv.py file=waveform.csv trace=1 period=80n
```


```
# get trace data from another column of CSV file
./send_csv.py file=waveform.csv trace=1 tcol=2 ycol=5

# program multiple channels from different columns in same CSV file, watch csv file for changes
./send_csv.py file=waveform.csv \
  tcol=0 \
  ch1col=1 \
  ch2col=2 \
  ch3col=3 \
  ch4col=4 \
  watch_changes=1
```
optional parameters/standard values:
```
file=<none>
delimiter=","
sample_rate=65e9
period=0
invert=0
idle_val=0
trace=1
delay=0
xscale=1
yscale=1
ip=192.168.0.203
watch_changes=0
tcol=0
ycol=1
ch1col=""
ch2col=""
ch3col=""
ch4col=""
```

- If watch_changes is set to 1, then script will not terminate but continue watching the CSV file for changes.
If a change is detected, the AWG will be re-programmed automatically.



## send_ltspice.py

### single channel example

- read in LTSpice .raw file (binary simulation output file, containing all voltages and currents)
- waveform is resampled/interpolated and then sent to AWG

example circuit - models a typical PMT signal

![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/spice_asc.png)

example circuit - simulated waveform

![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/spice_raw.png)

measured waveform from AWG

![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/spice_scope.png)

example usage:
```
./send_ltspice.py trace=1 file=ltspice_example/example.raw signal="V(output)"
```
optional parameters/standard values:
```
file=<none>
sample_rate=65e9
period=0
signal="V(output)"
invert=0
idle_val=0
trace=1
delay=0e-9
xscale=1
yscale=1
ip=192.168.0.203
watch_changes=0
```

### multi channel example

example circuit - four different uses of the LTSpice voltage source

![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/multichan_asc.png)

example circuit simulated waveforms

![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/multichan_raw.png)

measured waveforms from AWG

![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/multichan_scope_zoom.png)

example usage:
```
./send_ltspice.py file=ltspice_example/example_multichan.raw \
  signal1="V(out1)" \
  signal2="V(out2)" \
  signal3="V(out3)" \
  signal4="V(out4)" \
  watch_changes=1
```

- If watch_changes is set to 1, then script will not terminate but continue watching the .raw file for changes.
If a change is detected, the AWG will be re-programmed automatically.

![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/watch_changes.png)


## Acknowledgements

Thanks to Nuno Brum for the beautiful LTSpice RawReader module!
https://pypi.org/project/PyLTSpice/

