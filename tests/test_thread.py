# -*- coding: utf-8 -*-

"""Unittests for Janitoo thread.
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

import warnings
warnings.filterwarnings("ignore")

import sys, os
import time, datetime
import unittest
import threading
import logging
from pkg_resources import iter_entry_points

from janitoo_nosetests.server import JNTTServer, JNTTServerCommon
from janitoo_nosetests.thread import JNTTThread, JNTTThreadCommon
from janitoo_nosetests.thread import JNTTThreadRun, JNTTThreadRunCommon
from janitoo_nosetests.component import JNTTComponent, JNTTComponentCommon

from janitoo.utils import json_dumps, json_loads
from janitoo.utils import HADD_SEP, HADD
from janitoo.utils import TOPIC_HEARTBEAT
from janitoo.utils import TOPIC_NODES, TOPIC_NODES_REPLY, TOPIC_NODES_REQUEST
from janitoo.utils import TOPIC_BROADCAST_REPLY, TOPIC_BROADCAST_REQUEST
from janitoo.utils import TOPIC_VALUES_USER, TOPIC_VALUES_CONFIG, TOPIC_VALUES_SYSTEM, TOPIC_VALUES_BASIC

from janitoo_raspberry_i2c.thread_i2c import RpiI2CThread
import janitoo_raspberry_i2c_pca9685.bus_pca9685
import janitoo_raspberry_i2c_pca9685.pca9685

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_DISCOVERY = 0x5000

assert(COMMAND_DESC[COMMAND_DISCOVERY] == 'COMMAND_DISCOVERY')
##############################################################

class TestPca9685Thread(JNTTThreadRun, JNTTThreadRunCommon):
    """Test the thread
    """
    thread_name = "rpii2c"
    conf_file = "tests/data/janitoo_raspberry_i2c_pca9685.conf"

    def test_101_servo_angle(self):
        self.onlyRasperryTest()
        self.thread.start()
        try:
            timeout = 120
            i = 0
            while i< timeout and not self.thread.nodeman.is_started:
                time.sleep(1)
                i += 1
                print self.thread.nodeman.state
            print self.thread.bus.nodeman.nodes
            time.sleep(5)
            self.assertTrue(self.thread.nodeman.is_started)
            self.assertNotEqual(None, self.thread.bus.nodeman.find_node('servo'))
            self.assertNotEqual(None, self.thread.bus.find_components('rpii2c.servo'))
            servos = self.thread.bus.find_components('rpii2c.servo')
            self.assertEqual(1, len(servos))
            servo = servos[0]
            self.assertNotEqual(None, servo)
            servo.set_angle(0, 0, '0|0|180', 0)
            time.sleep(2)
            servo.set_angle(0, 0, '45|0|180', 0)
            time.sleep(2)
            servo.set_angle(0, 0, '90|0|180', 0)
            time.sleep(2)
            servo.set_angle(0, 0, '135|0|180', 0)
            time.sleep(2)
            servo.set_angle(0, 0, '180|0|180', 0)
            time.sleep(2)
            servo.set_angle(0, 0, '135|0|180', 0)
            time.sleep(2)
            servo.set_angle(0, 0, '90|0|180', 0)
            time.sleep(2)
            servo.set_angle(0, 0, '45|0|180', 0)
            time.sleep(2)
            servo.set_angle(0, 0, '0|0|180', 0)
        finally:
            self.thread.stop()
