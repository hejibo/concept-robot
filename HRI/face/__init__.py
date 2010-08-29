#!/usr/bin/python

# Lighthead-bot programm is a HRI PhD project at 
#  the University of Plymouth,
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



#
# FACE MODULE
#
# This module handles motion of the facial features.
# 
# MODULES IO:
#===========
# INPUT: - vision (eye orientation for eyelid position) [event]
#        - affect (facial expressions) [event]
#        - planner (..eventually)
#

import sys, random, time
import collections
import asyncore
import logging

LOG = logging.getLogger("face-srv")
LOG.setLevel(logging.DEBUG)

import comm
import conf

class FaceProtocolError(comm.ProtocolError):
    pass

class FaceError(comm.CmdError):
    pass

class FaceComm(object):
    """Remote connection handler: protocol parser."""
    
    def __init__(self, *args):
        self.fifo = collections.deque()

    def cmd_AU(self, argline):
        """if empty, returns current values. Otherwise, set them.
         argline: sending_module AU_name  target_value  duration.
        """
        if len(argline):
            try:
                au_name, value, duration = argline.split()[:3]
                self.fifo.append((au_name, float(value), float(duration)))
            except FloatException:
                raise FaceProtocolError("[AU] invalid float argument")
        else:
            msg = ""
            AU_info = self.server.get_all_AU()
            AU_info.sort()
            # name, target, duration
            for triplet in AU_info:
                msg += "AU {0[0]:5s} {0[1]} {0[2]:.3f}\n".format(triplet)
            self.send_msg(str(msg))


    def cmd_commit(self, argline):
        """Commit buffered updates"""
        for au, target, attack in self.fifo:
            try:
                self.server.set_AU(au, target, attack)
            except KeyError, e:
                raise FaceError("[AU] bad argument line:'%s', AU %s not found",
                                au+" %f %f" % (target, attack), e)
        self.fifo.clear()

    # def cmd_start(self, argline):
    #     try:
    #         start = float(argline.strip())
    #     except Exception, e:
    #         LOG.warning("[origin] bad argument line:'%s', caused: %s" %
    #                     (argline,e) )

    #     self.start_time = float(start)
    #     if self.start_time - time.time() < 0:
    #         LOG.warning("[origin] time received is elapsed: [r:%s c:%f]" %
    #                     (start, time.time()) )
    #     if self.start_time - time.time() > 30:
    #         LOG.warning("[origin] time received > 30s in future %s" % start)



class Face(object):
    """Main facial feature animation module

    Also maintains consistent muscle activation.
    AU value is normalized: 0 -> AU not streched, 1 -> stretched to max
    Setting an AU target value overwrites previous target.
    On target overwrite, interpolation starts from current value.
    """

    def __init__(self):
        self.AUs = {}

    def get_all_AU(self):
        return [(item[0],item[1][0],item[1][1])for item in self.AUs.iteritems()]

    def get_AU(self, name):
        return self.AUs[name]

    def set_available_AUs(self, available_AUs):
        """Define list of AUs available for a specific face.
         available_AUs: list of AU names.
        """
        for name in available_AUs:
            # target_coeffs, duration, elapsed, value
            self.AUs[name] = [(0,0) , .0 , .0, .0]
        LOG.info("Available AUs: %s" % sorted(self.AUs.keys()))

    def set_AU(self, name, target_value, duration):
        """Set targets for a specific AU, giving priority to specific inputs.
         name: AU name
         target_value: normalized value
         duration: time in seconds
        """
        duration = max(duration, .001)
        if self.AUs.has_key(name):
            self.AUs[name][:3] = (
                ((target_value-self.AUs[name][3])/duration, self.AUs[name][3]),
                duration, 0)
        else:
            self.AUs[name+'R'][:3] = (
                ((target_value-self.AUs[name+'R'][3])/duration,
                 self.AUs[name+'R'][3]), duration, 0)
            self.AUs[name+'L'][:3] = (
                ((target_value-self.AUs[name+'L'][3])/duration,
                 self.AUs[name+'L'][3]), duration, 0)

    def solve(self):
        """Here we can set additional checks (eg. AU1 vs AU4, ...)
        """

    def update(self, time_step):
        """Update AU values. This function shall be called for each frame.
         time_step: time in seconds elapsed since last call.
        """
        #TODO: motion dynamics
        to_update = collections.deque()
        for id,info in self.AUs.iteritems():
            coeffs, duration, elapsed, value = info
            target = coeffs[0] * duration + coeffs[1]
            elapsed += time_step
            if elapsed >= duration:      # keep timing
                if value != target:
                    self.AUs[id][2:] = duration, target
                    to_update.append((id, target))
                continue

            up_value = coeffs[0] * elapsed + coeffs[1]
            self.AUs[id][2:] = elapsed, up_value
            to_update.append((id, up_value))
        return to_update



if __name__ == '__main__':
    conf.name = sys.argv[-1]
    conf.load()
    try:
        server = comm.create_server(FaceServer, FaceClient, conf.conn_face)
    except UserWarning, err:
        comm.LOG.error("FATAL ERROR: %s (%s)", sys.argv[0], err)
        exit(-1)
    server.serve_forever()
    LOG.debug("Face server done")
