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
__copyright__ = "Copyright © 2013-2014-2015-2016 Sébastien GALLET aka bibi21000"

import logging
logger = logging.getLogger(__name__)

from janitoo.component import JNTComponent

try:
    from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_StepperMotor, Adafruit_DCMotor
except IOError:

    class Adafruit_MotorHAT(object):
        """ Fake class to allow buil on Continuous Integration tools.
        """
        pass

    class Adafruit_StepperMotor(object):
        """ Fake class to allow buil on Continuous Integration tools.
        """
        pass

    class Adafruit_DCMotor(object):
        """ Fake class to allow buil on Continuous Integration tools.
        """
        pass

    logger.exception("Can't import Adafruit_MotorHAT")

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_MOTOR = 0x3100
COMMAND_SWITCH_MULTILEVEL = 0x0026
COMMAND_SWITCH_BINARY = 0x0025

assert(COMMAND_DESC[COMMAND_SWITCH_MULTILEVEL] == 'COMMAND_SWITCH_MULTILEVEL')
assert(COMMAND_DESC[COMMAND_SWITCH_BINARY] == 'COMMAND_SWITCH_BINARY')
assert(COMMAND_DESC[COMMAND_MOTOR] == 'COMMAND_MOTOR')
##############################################################

from janitoo_raspberry_i2c import OID

def make_dcmotor(**kwargs):
    return DcMotorComponent(**kwargs)

def make_pwm(**kwargs):
    return PwmComponent(**kwargs)

def make_stepmotor(**kwargs):
    return StepMotorComponent(**kwargs)

def make_servo(**kwargs):
    return ServoComponent(**kwargs)

class DcMotorComponent(JNTComponent):
    """ A DC motor component for gpio """

    def __init__(self, bus=None, addr=None, **kwargs):
        """
        """
        oid = kwargs.pop('oid', '%s.dcmotor'%OID)
        name = kwargs.pop('name', "Motor")
        product_name = kwargs.pop('product_name', "Motor")
        product_type = kwargs.pop('product_type', "DC Motor")
        JNTComponent.__init__(self, oid=oid, bus=bus, addr=addr, name=name,
                product_name=product_name, product_type=product_type, **kwargs)
        logger.debug("[%s] - __init__ node uuid:%s", self.__class__.__name__, self.uuid)
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
            help="The max speed supported by the motor. Some motor doesn't seems support 100% PWM. A byte from 0 to 255",
            label='Speed',
            default=255,
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
        poll_value = self.values[uuid].create_poll_value(default=300)
        self.values[poll_value.uuid] = poll_value

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
        try:
            m = self.values['num'].get_data_index(index=index)
            if m is not None:
                self._bus.i2c_acquire()
                try:
                    self._bus.pca9685_manager.getMotor(m).setSpeed(data)
                finally:
                    self._bus.i2c_release()
        except Exception:
            logger.exception('[%s] - Exception when setting speed')

    def set_action(self, node_uuid, index, data):
        """Act on the motor
        """
        params = {}
        if data == "forward":
            try:
                m = self.values['num'].get_data_index(index=index)
                if m is not None:
                    self._bus.i2c_acquire()
                    try:
                        self._bus.pca9685_manager.getMotor(m).run(Adafruit_MotorHAT.FORWARD)
                    finally:
                        self._bus.i2c_release()
            except Exception:
                logger.exception('[%s] - Exception when running forward')
        elif data == "backward":
            try:
                m = self.values['num'].get_data_index(index=index)
                if m is not None:
                    self._bus.i2c_acquire()
                    try:
                        self._bus.pca9685_manager.getMotor(m).run(Adafruit_MotorHAT.BACKWARD)
                    finally:
                        self._bus.i2c_release()
            except Exception:
                logger.exception('[%s] - Exception when running backward')
        elif data == "release":
            m = self.values['num'].get_data_index(index=index)
            if m is not None:
                try:
                    self._bus.i2c_acquire()
                    try:
                        self._bus.pca9685_manager.getMotor(m).run(Adafruit_MotorHAT.RELEASE)
                    finally:
                        self._bus.i2c_release()
                except Exception:
                    logger.exception('[%s] - Exception when releasing one motor %s', self.__class__.__name__, m)

class StepMotorComponent(JNTComponent):
    """ A stepper motor component"""

    def __init__(self, bus=None, addr=None, **kwargs):
        """
        """
        oid = kwargs.pop('oid', '%s.stepmotor'%OID)
        name = kwargs.pop('name', "Motor")
        product_name = kwargs.pop('product_name', "Motor")
        product_type = kwargs.pop('product_type', "Step Motor")
        product_manufacturer = kwargs.pop('product_manufacturer', "Janitoo")
        JNTComponent.__init__(self, oid=oid, bus=bus, addr=addr, name=name,
                product_name=product_name, product_type=product_type, product_manufacturer=product_manufacturer, **kwargs)
        logger.debug("[%s] - __init__ node uuid:%s", self.__class__.__name__, self.uuid)

class PwmComponent(JNTComponent):
    """ A led driver component"""

    def __init__(self, bus=None, addr=None, **kwargs):
        """
        """
        oid = kwargs.pop('oid', '%s.pwm'%OID)
        name = kwargs.pop('name', "Motor")
        product_name = kwargs.pop('product_name', "PWM channel")
        product_type = kwargs.pop('product_type', "PWM channel")
        product_manufacturer = kwargs.pop('product_manufacturer', "Janitoo")
        JNTComponent.__init__(self, oid=oid, bus=bus, addr=addr, name=name,
                product_name=product_name, product_type=product_type, product_manufacturer=product_manufacturer, **kwargs)
        logger.debug("[%s] - __init__ node uuid:%s", self.__class__.__name__, self.uuid)
        uuid="level"
        self.values[uuid] = self.value_factory['action_switch_multilevel'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The level of the LED. A byte from 0 to 100',
            label='Level',
            default=0,
            set_data_cb=self.set_level,
        )
        poll_value = self.values[uuid].create_poll_value(default=300)
        self.values[poll_value.uuid] = poll_value
        uuid="max_level"
        self.values[uuid] = self.value_factory['config_byte'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help="The max level supported by the LED. Some LED doesn't seems support 100% PWM. A byte from 0 to 100",
            label='Max level',
            default=100,
        )
        uuid="num"
        self.values[uuid] = self.value_factory['config_byte'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The number of the LED on the board. A byte from 0 to 15',
            label='Num.',
        )
        uuid="switch"
        self.values[uuid] = self.value_factory['action_switch_binary'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            set_data_cb=self.set_switch,
        )
        poll_value = self.values[uuid].create_poll_value(default=300)
        self.values[poll_value.uuid] = poll_value

    def set_level(self, node_uuid, index, data):
        """Set the level ot the LED
        """
        p = self.values['num'].get_data_index(index=index)
        self._bus.i2c_acquire()
        try:
            self._bus.pca9685_manager.set_pwm(p, int(data*4096/100),0)
            self.values['level'].set_data_index(index=index, data=data)
        except Exception:
            logger.warning("[%s] - set_level invalid data : %s", self.__class__.__name__, data)
        finally:
            self._bus.i2c_release()

    def set_switch(self, node_uuid, index, data):
        """Switch On/Off the led
        """
        if data == "on":
            self._bus.i2c_acquire()
            try:
                p = self.values['num'].get_data_index(index=index)
                self._bus.pca9685_manager.set_pwm(p, 4096, 0)
                self.values['level'].set_data_index(index=index, data=100)
            except Exception:
                logger.exception('[%s] - Exception when switching on', self.__class__.__name__)
            finally:
                self._bus.i2c_release()
        elif data == "off":
            self._bus.i2c_acquire()
            try:
                p = self.values['num'].get_data_index(index=index)
                self._bus.pca9685_manager.set_pwm(p, 0, 4096)
                self.values['level'].set_data_index(index=index, data=0)
            except Exception:
                logger.exception('[%s] - Exception when switching off', self.__class__.__name__)
            finally:
                self._bus.i2c_release()
        else:
            logger.warning("[%s] - set_switch unknown data : %s", self.__class__.__name__, data)

class ServoComponent(JNTComponent):
    """ A servo component"""

    def __init__(self, bus=None, addr=None, **kwargs):
        """
        """
        oid = kwargs.pop('oid', '%s.servo'%OID)
        name = kwargs.pop('name', "Servo")
        product_name = kwargs.pop('product_name', "Servo")
        product_type = kwargs.pop('product_type', "Servo")
        product_manufacturer = kwargs.pop('product_manufacturer', "Janitoo")
        JNTComponent.__init__(self, oid=oid, bus=bus, addr=addr, name=name,
                product_name=product_name, product_type=product_type, product_manufacturer=product_manufacturer, **kwargs)
        logger.debug("[%s] - __init__ node uuid:%s", self.__class__.__name__, self.uuid)
        uuid="num"
        self.values[uuid] = self.value_factory['config_byte'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The number of the servo on board. A byte from 0 to 15',
            label='Num.',
        )
        uuid="pulse_min"
        self.values[uuid] = self.value_factory['config_integer'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The minimal pulse',
            label='Pulsemin',
            default=200,
        )
        uuid="pulse_max"
        self.values[uuid] = self.value_factory['config_integer'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The maximal pulse',
            label='Pulsemax',
            default=700,
        )
        uuid="angle"
        self.values[uuid] = self.value_factory['action_string'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            set_data_cb=self.set_angle,
            help='Set the angle of the servo. Format is value|angle_min|angle_max',
            label='angle',
        )
        poll_value = self.values[uuid].create_poll_value(default=300)
        self.values[poll_value.uuid] = poll_value

    def translate(self, value, left_min, left_max, right_min=None, right_max=None):
        """ Translate a value in a range to a value in the  servo's limits
        """
        if right_min is None:
            right_min = self.values['pulse_min'].data
        if right_max is None:
           right_max = self.values['pulse_max'].data
        # Figure out how 'wide' each range is
        left_span = left_max - left_min
        right_span = right_max - right_min
        # Convert the left range into a 0-1 range (float)
        value_scaled = float(value - left_min) / float(left_span)
        # Convert the 0-1 range into a value in the right range.
        return int(right_min + (value_scaled * right_span))

    def set_angle(self, node_uuid, index, data, pin=None):
        """ Change the angle of the servo
        """
        self._bus.i2c_acquire()
        try:
            if pin is None:
                pin = self.values['num'].data
            angle, angle_min, angle_max = data.split('|')
            value = self.translate(float(angle), float(angle_min), float(angle_max))
            logger.debug('[%s] - set_angle on pin %s to %s', self.__class__.__name__, pin, angle)
            self._bus.pca9685_manager.set_pwm(pin, 0, value)
            self.values['angle']._data = data
        except Exception:
            logger.exception('[%s] - Exception when set_angle', self.__class__.__name__)
        finally:
            self._bus.i2c_release()
