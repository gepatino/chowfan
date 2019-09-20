#!/usr/bin/env python3
import logging
import re
import subprocess
import time


DEFAULT_MAX_TEMP = 55
DEFAULT_POLLING_TIME = 5
SPEED_MAP = (  # (level, max_speed)
    (0, 0),
    (1, 2250),
    (2, 3200),
    (3, 3400),
    (4, 3550),
    (5, 4050),
    (6, 4450),
    (7, 4500),
)


class FanController:
    FAN_SPEED_MIN = 0
    FAN_SPEED_MAX = 7
    FAN_SPEED_INITIAL = 7

    def __init__(self, name):
        self.logger = logging.getLogger('FanController')
        self.name = name
        self.level = 0
        self.set_level(self.FAN_SPEED_INITIAL)

    def get_fan_rpm(self):
        proc = subprocess.run('sensors', stdout=subprocess.PIPE)
        output = proc.stdout.decode('utf-8').split('\n')
        regex = r'([0-9]+) RPM'
        fan_rpm = None
        for line in output:
            if line.startswith(self.name):
                matches = re.search(regex, line)
                if matches:
                    t = matches.groups()[0]
                    fan_rpm = int(t)
                break
        return fan_rpm

    def refresh_speed(self):
        rpm = self.get_fan_rpm()
        self.level = self.FAN_SPEED_MAX
        for level, max_rpm in SPEED_MAP:
            if rpm <= max_rpm:
                self.level = level
                break

    def _limit_level(self, level):
        level = min(level, self.FAN_SPEED_MAX)
        level = max(level, self.FAN_SPEED_MIN)
        return level

    def set_level(self, new_level):
        new_level = self._limit_level(new_level)
        if new_level != self.level:
            self.logger.info('Setting fan level to %s', new_level)
            with open('/proc/acpi/ibm/fan', 'w') as f:
                f.write('level {}'.format(new_level))
            self.level = new_level

    def set_relative_level(self, diff):
        new_level = self.level + diff
        self.set_level(new_level)

    def step_up(self):
        self.set_relative_level(1)

    def step_down(self):
        self.set_relative_level(-1)


class ChowFan:
    def __init__(self, fan_controller, max_temp=DEFAULT_MAX_TEMP, polling_time=DEFAULT_POLLING_TIME):
        self.max_temp = max_temp
        self.polling_time = polling_time
        self.ignore_sensors = []
        self.fan_controller = fan_controller

    def get_temps(self):
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
        return temps

    def get_max_temp(self):
        temps = self.get_temps()
        if not temps:
            return
        return max(temps)

    def get_avg_temp(self):
        temps = self.get_temps()
        if not temps:
            return
        return sum(temps) / len(temps)

    def run(self):
        prev_temp = self.get_max_temp()
        while True:
            time.sleep(self.polling_time)
            # temp = self.get_max_temp()
            temp = self.get_avg_temp()

            self.fan_controller.refresh_speed()

            # If it's hot and hotter than before, increase fan speed
            if temp > self.max_temp and temp > prev_temp:
                self.fan_controller.step_up()

            # If it's cold and colder or equal than before, decrease fan speed
            if temp < self.max_temp and temp <= prev_temp:
                self.fan_controller.step_down()

            prev_temp = temp


def main():
    logging.basicConfig(level=logging.INFO)
    fan_controller = FanController('fan1')
    chow_fan = ChowFan(fan_controller, polling_time=20)
    try:
        # chow_fan.ignore_sensors.append('acpitz-acpi-0')
        chow_fan.run()
    finally:
        print('Reverting fan level to auto')
        fan_controller.set_level('auto')


if __name__ == '__main__':
    main()
