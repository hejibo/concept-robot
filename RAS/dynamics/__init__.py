#!/usr/bin/python
# -*- coding: utf-8 -*-

# LightHead programm is a HRI PhD project at the University of Plymouth,
#  a Robotic Animation System including face, eyes, head and other
#  supporting algorithms for vision and basic emotions.
# Copyright (C) 2010 Frederic Delaunay, frederic.delaunay@plymouth.ac.uk

#  This program is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   General Public License for more details.

#  You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
DYNAMICS MODULE

 This module controls the robot's motion/speed using bijective functions and
their derivative. Currently a single instance of the dynamics module exists
across the whole system as other modules simply access this module's . This could be later changed if need

 With this module, the HMS can update the dynamics of the robot in realtime,
without changing initial and target states.

 Updating the dynamics function is totally transparent for the RAS modules, but
there may be obvious visual side-effects if the functions are very different.
"""

from utils import get_logger
from utils.comm import ASCIIRequestHandler
from utils.dynamics import Dynamics,ENTRIES

import RAS

__all__ = ['Dynamics']

LOG = get_logger(__package__)
DYNAMICS = ENTRIES['smooth_step1']

class DynamicsError(StandardError):
  pass


class Dynamics_Handler(ASCIIRequestHandler):
  """
  """

  def setup(self):
    self.fifo = deque()

  def cmd_list(self, argline):
    """Reply with names of available dynamics.
    """
    self.send_msg(', '.join(ENTRIES.iterkeys()))

  def cmd_use(self, argline):
    """Set a specific function to be used.
    """
    if argline not in Dynamics.ENTRIES.keys():
      LOG.warning("dynamic function '%s' doesn't exist", argline)
      return
    DYNAMICS = ENTRIES[argline.strip()]


class Dynamics_Server(object):
  """
  """
  pass