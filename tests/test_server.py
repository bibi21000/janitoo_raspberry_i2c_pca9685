# -*- coding: utf-8 -*-

"""Unittests for Janitoo-Raspberry Pi Server.
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

import sys, os
import time, datetime
import unittest
import threading
import logging
from pkg_resources import iter_entry_points

from janitoo_nosetests.server import JNTTServer, JNTTServerCommon
from janitoo_nosetests.thread import JNTTThread, JNTTThreadCommon

from janitoo.utils import json_dumps, json_loads
from janitoo.utils import HADD_SEP, HADD
from janitoo.utils import TOPIC_HEARTBEAT
from janitoo.utils import TOPIC_NODES, TOPIC_NODES_REPLY, TOPIC_NODES_REQUEST
from janitoo.utils import TOPIC_BROADCAST_REPLY, TOPIC_BROADCAST_REQUEST
from janitoo.utils import TOPIC_VALUES_USER, TOPIC_VALUES_CONFIG, TOPIC_VALUES_SYSTEM, TOPIC_VALUES_BASIC

from janitoo_raspberry.server import PiServer

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_DISCOVERY = 0x5000

assert(COMMAND_DESC[COMMAND_DISCOVERY] == 'COMMAND_DISCOVERY')
##############################################################

#~ JNTTServer.skipRasperryTest()

class TestPiSerser(JNTTServer, JNTTServerCommon):
    """Test the pi server
    """
    loglevel = logging.DEBUG
    path = '/tmp/janitoo_test'
    broker_user = 'toto'
    broker_password = 'toto'
    server_class = PiServer
    server_conf = "tests/data/janitoo_raspberry_i2c_hat.conf"

    def test_101_wait_for_all_nodes(self):
        self.start()
        try:
            self.assertHeartbeatNode(hadd=HADD%(139,0))
            self.assertHeartbeatNode(hadd=HADD%(139,1))
            self.assertHeartbeatNode(hadd=HADD%(139,2))
        finally:
            self.stop()

    def test_111_server_start_no_error_in_log(self):
        self.onlyRasperryTest()
        self.start()
        try:
            time.sleep(120)
            self.assertInLogfile('Found heartbeats in timeout')
            self.assertNotInLogfile('^ERROR ')
        finally:
            self.stop()

    def test_112_request_nodes_and_values(self):
        self.onlyRasperryTest()
        self.start()
        try:
            self.assertHeartbeatNode()
            time.sleep(5)
            for request in NETWORK_REQUESTS:
                self.assertNodeRequest(cmd_class=COMMAND_DISCOVERY, uuid=request, node_hadd=HADD%(139,0), client_hadd=HADD%(9999,0))
        finally:
            self.stop()
