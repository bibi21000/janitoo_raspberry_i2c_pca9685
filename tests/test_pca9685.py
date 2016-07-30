# -*- coding: utf-8 -*-

"""Unittests for Janitoo-Roomba Server.
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
from janitoo_nosetests.component import JNTTComponent, JNTTComponentCommon

from janitoo.utils import json_dumps, json_loads
from janitoo.utils import HADD_SEP, HADD
from janitoo.utils import TOPIC_HEARTBEAT
from janitoo.utils import TOPIC_NODES, TOPIC_NODES_REPLY, TOPIC_NODES_REQUEST
from janitoo.utils import TOPIC_BROADCAST_REPLY, TOPIC_BROADCAST_REQUEST
from janitoo.utils import TOPIC_VALUES_USER, TOPIC_VALUES_CONFIG, TOPIC_VALUES_SYSTEM, TOPIC_VALUES_BASIC

import janitoo_raspberry_i2c_pca9685.bus_pca9685
import janitoo_raspberry_i2c_pca9685.pca9685

class TestDcMotorComponent(JNTTComponent, JNTTComponentCommon):
    """Test the component
    """
    component_name = "rpii2c.dcmotor"

class TestStepMotorComponent(JNTTComponent, JNTTComponentCommon):
    """Test the component
    """
    component_name = "rpii2c.stepmotor"

class TestPwmComponent(JNTTComponent, JNTTComponentCommon):
    """Test the component
    """
    component_name = "rpii2c.pwm"

class TestPanComponent(JNTTComponent, JNTTComponentCommon):
    """Test the component
    """
    component_name = "rpii2c.pan"

class TestServoComponent(JNTTComponent, JNTTComponentCommon):
    """Test the component
    """
    component_name = "rpii2c.servo"

    def test_101_translate(self):
        entries = iter_entry_points(group='janitoo.components', name=self.component_name)
        entry = entries.next()
        mkth = entry.load()
        compo = mkth()
        self.assertEqual(compo.translate(1, 1, 10, 1, 100), 1)
        self.assertEqual(compo.translate(10, 1, 10, 1, 100), 100)
        self.assertEqual(compo.translate(2, 1, 3, 1, 30), 15)
        self.assertEqual(compo.translate(3, 1, 5, 1, 100), 50)
        self.assertEqual(compo.translate(5, 0, 10, 0, 100), 50)
