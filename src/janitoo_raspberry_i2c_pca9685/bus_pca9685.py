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
__copyright__ = "Copyright © 2013-2014-2015-2016 Sébastien GALLET aka bibi21000"

# Set default logging handler to avoid "No handler found" warnings.
import logging
logger = logging.getLogger(__name__)

try:
    from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_StepperMotor, Adafruit_DCMotor
    from Adafruit_MotorHAT.Adafruit_PWM_Servo_Driver import PWM
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

    class PWM(object):
        """ Fake class to allow buil on Continuous Integration tools.
        """
        pass

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

from janitoo_raspberry_i2c import OID

def extend( self ):

    uuid="%s_addr"%OID
    self.values[uuid] = self.value_factory['config_integer'](options=self.options, uuid=uuid,
        node_uuid=self.uuid,
        help='The I2C address of the pca9685 board',
        label='Addr',
        default=0x40,
    )
    uuid="%s_freqency"%OID
    self.values[uuid] = self.value_factory['config_integer'](options=self.options, uuid=uuid,
        node_uuid=self.uuid,
        help='The frequency for pwm',
        label='Freq.',
        default=1600,
        units="Hz",
    )
    self.export_values()
    self.pca9685_manager = None
    self.export_attrs('pca9685_manager', self.pca9685_manager)

    self._pca9685_start = self.start
    def start(mqttc, trigger_thread_reload_cb=None):
        """Start the bus"""
        logger.debug("[%s] - Start the bus %s on address %s", self.__class__.__name__, self.oid, self.values["%s_addr"%OID].data )
        self.i2c_acquire()
        try:
            self.pca9685_manager = Pca9685Manager(addr=self.values["%s_addr"%OID].data, freq=self.values["%s_freqency"%OID].data)
        except Exception:
            logger.exception('[%s] - Exception when intialising pca9685 board', self.__class__.__name__)
        finally:
            self.i2c_release()
        self.update_attrs('pca9685_manager', self.pca9685_manager)
        return self._pca9685_start(mqttc, trigger_thread_reload_cb=trigger_thread_reload_cb)
    self.start = start

    self._pca9685_stop = self.stop
    def stop():
        """Stop the bus"""
        if self.pca9685_manager is not None:
            self.i2c_acquire()
            try:
                self.pca9685_manager.software_reset()
            except Exception:
                logger.exception('[%s] - Exception when stopping pca9685 board', self.__class__.__name__)
            finally:
                self.i2c_release()
        ret = self._pca9685_stop()
        self.pca9685_manager = None
        self.update_attrs('pca9685_manager', self.pca9685_manager)
        return ret
    self.stop=stop


class Pca9685Manager(Adafruit_MotorHAT):
    """To share bus with the adafruit library.
    Maybe we must control the pin use (ie to not activate a led on the
    """

    def __init__(self, addr = 0x40, freq = 1600):
        """Init
        """
        self._i2caddr = addr        # default addr
        self._frequency = freq      # default @1600Hz PWM freq
        self._motors = None
        self._steppers = None
        self._leds = None
        self._pwm = PWM(addr, debug=False)
        self._pwm.setPWMFreq(self._frequency)

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

    def set_pwm(self, pin, value_on):
        """
        """
        if (pin < 0) or (pin > 15):
            raise NameError('PWM pin must be between 0 and 15 inclusive')
        if (value_on < 0) and (value_on > 4096):
            raise NameError('Pin value must be between 0 and 4096!')
        value_off = 4096 - value_on
        self._pwm.setPWM(pin, value_on, value_off)
