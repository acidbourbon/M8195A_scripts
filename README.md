# M8195A_scripts

## pulser.py

![Photo](https://github.com/acidbourbon/M8195A_scripts/blob/master/pics/pulser.png)


example usage:
```
./pulser.py width=50e-9 trace=1 on_val=0.5 idle_val=0
./pulser.py width=30e-9 trace=2 on_val=-0.3 idle_val=0.1 delay=10e-9
```

optional parameters/standard values:
```
sample_rate=64e9
invert=0
on_val=0.5
idle_val=0
trace=1
width=50e-9
delay=0e-9
ip=192.168.0.203
```

## send_csv.py

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
sample_rate=64e9
invert=0
idle_val=0
trace=1
delay=0e-9
xscale=1
yscale=1
ip=192.168.0.203
```
