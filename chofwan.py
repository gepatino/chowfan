#!/usr/bin/env python3
import re
import time
import subprocess


class ChowFanController:
    def __init__(self, max_temp=50, min_fan_speed=0, max_fan_speed=7, initial_fan_speed=1, polling_time=10):
        self.max_temp = max_temp
        self.fan_speed = initial_fan_speed
        self.min_fan_speed = min_fan_speed
        self.max_fan_speed = max_fan_speed
        self.polling_time = polling_time
        self.ignore_sensors = []
        self.set_fan_level()

    def get_max_temp(self):
        proc = subprocess.run('sensors', stdout=subprocess.PIPE)
        output = proc.stdout.decode('utf-8').split('\n')
        regex = r'\+([0-9]+\.[0-9])°C'
        temps = []
        ignore_next = False
        for line in output:
            if line.strip() in self.ignore_sensors:
                ignore_next = True
            matches = re.search(regex, line)
            if matches:
                if not ignore_next:
                    t = matches.groups()[0]
                    temps.append(float(t))
                ignore_next = False
        if not temps:
            return

        return max(temps)

    def set_fan_level(self):
        if self.fan_speed in range(8):
            with open('/proc/acpi/ibm/fan', 'w') as f:
                f.write('level {}'.format(self.fan_speed))

    def run(self):
        while True:
            temp = self.get_max_temp()
            if temp:
                if temp > self.max_temp and self.fan_speed < self.max_fan_speed:
                    self.fan_speed += 1
                elif self.fan_speed > self.min_fan_speed:
                    self.fan_speed -= 1
                print('Temp: {} - Setting fan level to {}'.format(temp, self.fan_speed))
                self.set_fan_level()

            time.sleep(self.polling_time)
            

if __name__ == '__main__':
    controller = ChowFanController(max_temp=50, initial_fan_speed=7)
    controller.ignore_sensors.append('acpitz-virtual-0')
    controller.run()
