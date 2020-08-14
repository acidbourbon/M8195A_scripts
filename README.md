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

The Keysight M8195 consists of two parts: The hardware and the "Soft Front Panel" software.
This collection of scripts talks DOES NOT talk to the hardware directly (because the hardware is dumb),
but to the "Soft Front Panel", which provides the SCPI interface to the instrument as a whole.

The SCPI interface IS NOT running by default. "Soft Front Panel" needs to be started with command line
argument "/Socket 2025" in order for our scripts to work.

This is easily facilitated by creating a Desktop shortcut to the software and editing it, as shown below:

![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/soft_front_panel_arguments.png)

Then start the software via this shortcut.


## pulser.py

- generate square pulses with arbitrary "idle" and "on" levels (-0.5 to 0.5V)

![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/pulser.png)


example usage:
```
./pulser.py width=50e-9 trace=1 on_val=0.5 idle_val=0
./pulser.py width=30e-9 trace=2 on_val=-0.3 idle_val=0.1 delay=10e-9
```

optional parameters/standard values:
```
sample_rate=65e9
invert=0
on_val=0.5
idle_val=0
trace=1
width=50e-9
delay=0e-9
ip=192.168.0.203
```

## send_csv.py

- read in two column csv file and send it to the AWG
- first column is time in seconds
- second column is voltage in volts
- standard delimiter is "," but can be adjusted (see below)
- waveform is resampled/interpolated, so time steps can be arbitrary

![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/send_csv.png)

example usage:
```
./send_csv.py file=waveform.csv trace=1 
./send_csv.py file=waveform.csv trace=2 delay=10e-9 invert=1 yscale=0.5 xscale=0.3
```
optional parameters/standard values:
```
file=<none>
delimiter=","
sample_rate=65e9
invert=0
idle_val=0
trace=1
delay=0e-9
xscale=1
yscale=1
ip=192.168.0.203
```

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

