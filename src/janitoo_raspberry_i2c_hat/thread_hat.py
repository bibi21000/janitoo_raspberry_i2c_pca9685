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

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_CONTROLLER = 0x1050

assert(COMMAND_DESC[COMMAND_CONTROLLER] == 'COMMAND_CONTROLLER')
##############################################################

def make_hat(options):
    if get_option_autostart(options, 'rpii2chat') == True:
        return MotorHatThread(options)
    else:
        return None

def make_pca9685(options):
    if get_option_autostart(options, 'rpii2cpca9685') == True:
        return Pca9685Thread(options)
    else:
        return None

OIDHAT = 'rpii2chat'
OIDPCA9685 = 'rpii2cpca9685'

class MotorHatThread(JNTBusThread):
    """The basic thread

    """
    def init_bus(self):
        """Build the bus
        """
        from janitoo_raspberry_i2c_hat.bus_hat import MotorHatBus
        self.section = OIDHAT
        self.bus = MotorHatBus(options=self.options, oid=self.section, product_name="Raspberry Motor Hat board controller")

class Pca9685Thread(JNTBusThread):
    """The basic thread

    """
    def init_bus(self):
        """Build the bus
        """
        from janitoo_raspberry_i2c_hat.bus_pca9685 import Pca9685Bus
        self.section = OIDPCA9685
        self.bus = Pca9685(options=self.options, oid=self.section, product_name="Raspberry pca9685 board controller")

