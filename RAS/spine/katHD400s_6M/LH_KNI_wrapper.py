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
LightHead KNI wrapper using Python ctypes.
This file can only be used with LH_KNI_wrapper.cpp compiled to a shared library.
Refer to the README for further information.

Only basic control on the arm is needed. Avoiding swig also allows us to be
closer to low-level apis, hence reducing overhead.
"""
from os.path import dirname, sep
from ctypes import *

class LHKNI_wrapper(object):
    """
    """
    def __init__(self, KNI_cfg_file, address):
        try:
            self.KNI = CDLL(dirname(__file__)+sep+'libLH_KNI_wrapper-debug.so')
        except OSError, e:
            raise ImportError('trying to load shared object: '+e.args[0])
        
        if self.initKatana(KNI_cfg_file, address) == -1:
            raise SpineError('KNI configuration file not found or'
                             ' failed to connect to hardware', KNI_cfg_file)
        print 'loaded config file', KNI_cfg_file, 'and now connected'

    def __getattr__(self,name):
        """
        """
        return self.KNI.__getattr__(name)

    def getEncoder(self, axis):
        enc = c_int()
        self.KNI.getEncoder(axis, byref(enc))
        return enc
    
    def getEncoders(self):
        encs = (c_int * 6)()
        self.KNI.getEncoders(encs)
        return [ e for e in encs ]

    def getVelocities(self):
        vels = (c_int * 6)()
        self.KNI.getVelocities(vels)
        return [ v for v in vels ]

    def is_axis_moving(self, axis):
        return self.KNI.is_moving(axis)

    def is_moving(self):
        return self.KNI.is_moving(0)
