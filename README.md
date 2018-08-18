# chowfan
Python script to control Thinkpad fans

Sometimes, after waking up from sleep, fans keep working at full speed forever in Thinkpad notebooks. This is quite anoying both for the noise and baterry consumption.

A quick workaround is to sleep the notebook again and wake it up quickly, but it didn't worked for me some times.

So, I wrote this simple Python script that controls the fan speed according to the sensors reported temperature.
If the temperature is over a given threshold, fan speed is increased as long as the temperature keeps going up, until max speed is reached.
When the temperature goes below the given threshold, fan speed is decreased as long as the temperature keeps going down.

When the script is stopped, the fan control is returned to the auto setting, so it will probably start missbehaving again.

You can choose which sensors to use (or which ones to ignore), since I also found that when this bug happens, the `acpitz-virtual-0` sensor reports a fixed temperature (48C in my Thinkpad T470s), so you need to ignore it.

The scripts have several default values that made sense for me. 

TO DO: Add arguments for all options.

## Requiremnts

In order to have chowfan working, you must enable writing to the `thinkpad_acpi` controlled proc entry: `/proc/acpi/ibm/fan`.
To do this, edit or create the file `/etc/modprobe.d/thinkpad_acpi.conf` file, adding the following option:

```
options thinkpad_acpi fan_control=1
```

Then restart the module `thinkpad_acpi` or restart the computer (sometimes it's difficult to restart the module if it's being used or if it has too many dependencies).


## Usage

If your computer wakes up in a bad mood, give it some chowfan. Start the chowfan script using sudo and that's it, it will controll the fans for you:
```
$ cd <chofwan_dir>
$ sudo ./chowfan.py
```

If you prefer,an alias, add this to your `.bash_aliases`:
```
alias chowfan='cd <chowfan_dir>; sudo ./chowfan.py'
```
