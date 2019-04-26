#!/usr/bin/env python3
import logging
import re
import subprocess
import time


class ChowFanController:
    def __init__(self, max_temp=55, min_fan_speed=0, max_fan_speed=7, initial_fan_speed=7, polling_time=10):
        self.max_temp = max_temp
        self.fan_speed = initial_fan_speed
        self.min_fan_speed = min_fan_speed
        self.max_fan_speed = max_fan_speed
        self.polling_time = polling_time
        self.ignore_sensors = []

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

    def set_fan_level(self, level):
        with open('/proc/acpi/ibm/fan', 'w') as f:
            f.write('level {}'.format(level))

    def run(self):
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('ChowFanController')

        self.set_fan_level(self.fan_speed)
        prev_temp = self.get_max_temp()

        while True:
            time.sleep(self.polling_time)
            temp = self.get_max_temp()

            new_speed = self.fan_speed

            # If it's hot and hotter than before, increase fan speed
            if temp > self.max_temp and temp > prev_temp and self.fan_speed < self.max_fan_speed:
                new_speed += 1

            # If it's cold and colder or equal than before, decrease fan speed
            if temp < self.max_temp and temp <= prev_temp and self.fan_speed > self.min_fan_speed:
                new_speed -= 1

            if new_speed != self.fan_speed:
                logger.info('Temp: %.2f - Setting fan level to %s', temp, new_speed)
                self.set_fan_level(new_speed)
                self.fan_speed = new_speed
            else:
                logger.debug('Temp: %.2f - Keeping fan level at %s', temp, self.fan_speed)

            prev_temp = temp


def main():
    controller = ChowFanController()
    try:
        controller.ignore_sensors.append('acpitz-acpi-0')
        controller.run()
    finally:
        print('Reverting fan level to auto')
        controller.set_fan_level('auto')


if __name__ == '__main__':
    main()
