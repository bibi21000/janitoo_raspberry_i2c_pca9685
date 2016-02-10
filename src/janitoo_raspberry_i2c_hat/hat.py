# -*- coding: utf-8 -*-
"""The Raspberry bmp thread

Server files using the http protocol

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

import logging
logger = logging.getLogger(__name__)
import os, sys
import threading

from janitoo.thread import JNTBusThread, BaseThread
from janitoo.options import get_option_autostart
from janitoo.utils import HADD
from janitoo.node import JNTNode
from janitoo.value import JNTValue
from janitoo.component import JNTComponent
from janitoo_raspberry_i2c.bus_i2c import I2CBus

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_MOTOR = 0x3100

assert(COMMAND_DESC[COMMAND_MOTOR] == 'COMMAND_MOTOR')
##############################################################

def make_dcmotor(**kwargs):
    return DcMotorComponent(**kwargs)

def make_led(**kwargs):
    return LedComponent(**kwargs)

def make_stepmotor(**kwargs):
    return StepMotorComponent(**kwargs)

class DcMotorComponent(JNTComponent):
    """ A generic component for gpio """

    def __init__(self, bus=None, addr=None, **kwargs):
        """
        """
        oid = kwargs.pop('oid', 'rpii2c.dcmotor')
        name = kwargs.pop('name', "Motor")
        product_name = kwargs.pop('product_name', "Motor")
        product_type = kwargs.pop('product_type', "DC Motor")
        product_manufacturer = kwargs.pop('product_manufacturer', "Janitoo")
        JNTComponent.__init__(self, oid=oid, bus=bus, addr=addr, name=name,
                product_name=product_name, product_type=product_type, product_manufacturer="Janitoo", **kwargs)
        logger.debug("[%s] - __init__ node uuid:%s", self.__class__.__name__, self.uuid)
        uuid="label"
        self.values[uuid] = self.value_factory['config_string'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='A user friendly label for the motor',
            label='Label',
            default="Motor",
        )
        uuid="hexadd"
        self.values[uuid] = self.value_factory['config_string'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The I2C address of the motor HAT board',
            label='Addr',
            default="0x60",
        )
        uuid="speed"
        self.values[uuid] = self.value_factory['config_byte'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The speed of the motor. A byte from 0 to 255',
            label='Speed',
            default=0,
            set_data_cb=self.set_speed,
        )
        uuid="max_speed"
        self.values[uuid] = self.value_factory['config_byte'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The max speed supported by the motor. Some mo. A byte from 0 to 255',
            label='Speed',
            default="255",
        )
        uuid="num"
        self.values[uuid] = self.value_factory['config_byte'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The number of the motor on the Hat board. A byte from 1 to 4',
            label='Num.',
        )
        uuid="actions"
        self.values[uuid] = self.value_factory['action_list'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The action on the DC motor',
            label='Actions',
            list_items=['forward', 'backward', 'release'],
            default='release',
            set_data_cb=self.set_action,
            is_writeonly = True,
            cmd_class=COMMAND_MOTOR,
            genre=0x01,
        )
        uuid="current_speed"
        self.values[uuid] = self.value_factory['sensor_integer'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The current speed of the motor. An integer from -255 to 255',
            label='CSpeed',
            get_data_cb=self.get_current_speed,
        )
        self.hatboard = None

    def get_current_speed(self, node_uuid, index):
        """Get the current speed
        """
        current_state = self.values['actions'].get_data_index(index=index)
        if current_state == 'forward':
            return self.values['speed'].get_data_index(index=index)
        elif current_state == 'backward':
            return self.values['speed'].get_data_index(index=index) * -1
        else:
            return 0

    def set_speed(self, node_uuid, index, data):
        """Set the speed ot the motor
        """
        self.values['speed'].set_data_index(index=index, data=data)
        self._speed(index, data)

    def set_action(self, node_uuid, index, data):
        """Act on the motor
        """
        params = {}
        if data == "forward":
            self._forward(index)
        elif data == "backward":
            self._backward(index)
        elif data == "release":
            self._release(index)

    def _speed(self, index, data):
        """Change the speed of the DC motor"""
        try:
            m = self.values['num'].get_data_index(index=index)
            if m is not None:
                self.hatboard.getMotor(m).setSpeed(data)
        except:
            logger.exception('Exception when setting speed')

    def _forward(self, index):
        """Forward the DC motor"""
        try:
            m = self.values['num'].get_data_index(index=index)
            if m is not None:
                self.hatboard.getMotor(m).run(Adafruit_MotorHAT.FORWARD)
        except:
            logger.exception('Exception when running forward')

    def _backward(self, index):
        """Backward the DC motor"""
        try:
            m = self.values['num'].get_data_index(index=index)
            if m is not None:
                self.hatboard.getMotor(m).run(Adafruit_MotorHAT.BACKWARD)
        except:
            logger.exception('Exception when running backward')

    def _release(self, index):
        """Release the DC motor. If index == -1 release all motors"""
        if index == -1:
            for m in range(1,5):
                try:
                    self.hatboard.getMotor(m).run(Adafruit_MotorHAT.RELEASE)
                except:
                    logger.exception('Exception when releasing all motors')
        else:
            m = self.values['num'].get_data_index(index=index)
            if m is not None:
                try:
                    self.hatboard.getMotor(m).run(Adafruit_MotorHAT.RELEASE)
                except:
                    logger.exception('Exception when releasing one motor %s'%m)

    def check_heartbeat(self):
        """Check that the component is 'available'

        """
        return self.hatboard is not None

    def start(self, mqttc):
        """Start the component.

        """
        self.hatboard = Adafruit_MotorHAT(addr=self.values['hexadd'])
        JNTComponent.start(self, mqttc)
        self._release(-1)
        return True

    def stop(self):
        """Stop the component.

        """
        self._release(-1)
        JNTComponent.stop(self)
        return True


class StepMotorComponent(JNTComponent):
    """ A generic component for gpio """

    def __init__(self, bus=None, addr=None, **kwargs):
        """
        """
        oid = kwargs.pop('oid', 'rpii2c.stepmotor')
        name = kwargs.pop('name', "Motor")
        product_name = kwargs.pop('product_name', "Motor")
        product_type = kwargs.pop('product_type', "Step Motor")
        product_manufacturer = kwargs.pop('product_manufacturer', "Janitoo")
        JNTComponent.__init__(self, oid=oid, bus=bus, addr=addr, name=name,
                product_name=product_name, product_type=product_type, product_manufacturer="Janitoo", **kwargs)
        logger.debug("[%s] - __init__ node uuid:%s", self.__class__.__name__, self.uuid)

    def check_heartbeat(self):
        """Check that the component is 'available'

        """
        if 'temperature' not in self.values:
            return False
        return self.values['temperature'].data is not None

class LedComponent(JNTComponent):
    """ A generic component for gpio """

    def __init__(self, bus=None, addr=None, **kwargs):
        """
        """
        oid = kwargs.pop('oid', 'rpii2c.led')
        name = kwargs.pop('name', "Motor")
        product_name = kwargs.pop('product_name', "LED")
        product_type = kwargs.pop('product_type', "LED Driver")
        product_manufacturer = kwargs.pop('product_manufacturer', "Janitoo")
        JNTComponent.__init__(self, oid=oid, bus=bus, addr=addr, name=name,
                product_name=product_name, product_type=product_type, product_manufacturer="Janitoo", **kwargs)
        logger.debug("[%s] - __init__ node uuid:%s", self.__class__.__name__, self.uuid)

    def check_heartbeat(self):
        """Check that the component is 'available'

        """
        if 'temperature' not in self.values:
            return False
        return self.values['temperature'].data is not None
