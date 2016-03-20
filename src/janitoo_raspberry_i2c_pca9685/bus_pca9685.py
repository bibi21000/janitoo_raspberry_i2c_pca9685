# -*- coding: utf-8 -*-
"""The Raspberry camera worker

Installation :

.. code-block:: bash

    sudo apt-get install python-pycamera

"""

__license__ = """
    This file is part of Janitoo.

    Janitoo is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Janitoo is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Janitoo. If not, see <http://www.gnu.org/licenses/>.

"""
__author__ = 'Sébastien GALLET aka bibi21000'
__email__ = 'bibi21000@gmail.com'
__copyright__ = "Copyright © 2013-2014-2015 Sébastien GALLET aka bibi21000"

# Set default logging handler to avoid "No handler found" warnings.
import logging
logger = logging.getLogger(__name__)
import os, sys
import threading
import time
import datetime
import socket
from janitoo.thread import JNTBusThread
from janitoo.bus import JNTBus
from janitoo.component import JNTComponent
from janitoo.thread import BaseThread
from janitoo.options import get_option_autostart

from janitoo_raspberry_i2c_pca9685.thread_pca9685 import OID

try:
    from Adafruit_MotorHAT.Adafruit_PWM_Servo_Driver import PWM
    from Adafruit_MotorHAT import Adafruit_MotorHAT
except:
    logger.exception("Can't import Adafruit_MotorHAT")

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_CAMERA_PREVIEW = 0x2200
COMMAND_CAMERA_PHOTO = 0x2201
COMMAND_CAMERA_VIDEO = 0x2202
COMMAND_CAMERA_STREAM = 0x2203

assert(COMMAND_DESC[COMMAND_CAMERA_PREVIEW] == 'COMMAND_CAMERA_PREVIEW')
assert(COMMAND_DESC[COMMAND_CAMERA_PHOTO] == 'COMMAND_CAMERA_PHOTO')
assert(COMMAND_DESC[COMMAND_CAMERA_VIDEO] == 'COMMAND_CAMERA_VIDEO')
assert(COMMAND_DESC[COMMAND_CAMERA_STREAM] == 'COMMAND_CAMERA_STREAM')
##############################################################

class Pca9685Bus(JNTBus):
    """A pseudo-bus to handle the Raspberry pca9685 board
    """
    def __init__(self, **kwargs):
        """
        :param int bus_id: the SMBus id (see Raspberry Pi documentation)
        :param kwargs: parameters transmitted to :py:class:`smbus.SMBus` initializer
        """
        JNTBus.__init__(self, **kwargs)
        uuid="%s_hexadd"%OID
        self.values[uuid] = self.value_factory['config_string'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The I2C address of the pca9685 board',
            label='Addr',
            default="0x40",
        )
        self.pca9685 = None
        self.export_attrs('pca9685', self.pca9685)

    def start(self, mqttc, trigger_thread_reload_cb=None):
        JNTBus.start(self, mqttc, trigger_thread_reload_cb)
        try:
            self.pca9685 = Pca9685Manager(address=self.values["%s_hexadd"%OID].data)
        except:
            logger.exception('Exception when intialising pca9685 board')
        self.update_attrs('pca9685', self.pca9685)

    def stop(self):
        if self.pca9685 is not None:
            self.pca9685.software_reset()
        self.pca9685 = None
        self.update_attrs('pca9685', self.pca9685)
        JNTBus.stop(self)

    def check_heartbeat(self):
        """Check that the bus is 'available'

        """
        return self.pca9685 is not None

class Pca9685Manager(Adafruit_MotorHAT):
    """To share bus with the adafruit library
    """

    def __init__(self, addr = 0x40, freq = 1600):
        """Init
        """
        self._i2caddr = addr        # default addr
        self._frequency = freq      # default @1600Hz PWM freq
        self._motors = []
        self._steppers = []
        self._leds = []
        self._pwm =  PWM(addr, debug=False)
        self._pwm.setPWMFreq(self._frequency)

    @property
    def pwm(self):
        """
        """
        return self._pwm

    @property
    def motors(self):
        """
        """
        if self._motors is None:
            self._motors = [ Adafruit_DCMotor(self, m) for m in range(4) ]
        return self._motors

    @property
    def steppers(self):
        """
        """
        if self._steppers is None:
            self._steppers = [ Adafruit_StepperMotor(self, 1), Adafruit_StepperMotor(self, 2) ]
        return self._steppers

    def software_reset(self):
        """
        """
        self._pwm.softwareReset()

    def setPwm(self, pin, value_on):
        """
        """
        if (pin < 0) or (pin > 15):
            raise NameError('PWM pin must be between 0 and 15 inclusive')
        if (value_on < 0) and (value_on > 4096):
            raise NameError('Pin value must be between 0 and 4096!')
        value_off = 4096 - value_on
        self._pwm.setPWM(pin, value_on, value_off)
