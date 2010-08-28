#
# The spine module controls orientation and position of the robot torso and neck
# It provides a high-level API and relies on the backend implemented in the
#  module 'spine_backend'
#
# The API is limited to hardware implementation and indeed results are hardware-
#  dependant. However as long as the hardware provides the required DOF and
#  backend provides required functions, the end-result should be similar.
#

class NotImplemented(Exception):
    pass

class SpineException(Exception):
    pass


class SpineElementInfo(object):
    """Capabilities and Information about an element of the spine"""

    def __init__(self):
        self.origin = [.0,]*3   # global coordinates of origin
        self.limits_rot = []    # min and max orientation values for each axis
        self.limits_pos = []    # min and max position values for each axis
        self.rot = [None,]*3
        self.pos = [None,]*3

class TorsoInfo(SpineElementInfo):
    pass
class NeckInfo(SpineElementInfo):
    pass


class SpineClient(object):
    """
    """

    def cmd_rotate(self, argline):
        """relative rotation on 3 axis"""
        args = [ float(arg) for arg in argline.split(',') ]
        if not args:
            self.send_msg('head_rot %s' % self.server.get_neck_info().rot)
            return
        self.server.set_neck_rot_pos(rot_xyz=tuple(args))
        
    def cmd_move(self, argline):
        """relative position on 3 axis"""
        args = [ float(arg) for arg in argline.split(',') ]
        if not args:
            self.send_msg('head_pos %s' % self.server.get_neck_info().pos)
            return
        self.server.set_neck_rot_pos(pos_xyz=tuple(args))

    def cmd_commit(self, argline):
        pass


class SpineBase(object):
    """API for spine management (includes neck)."""

    def __init__(self):
        """torso_info and neck_info are readonly properties"""
        self._torso_info = TorsoInfo()
        self._neck_info  = NeckInfo()
        self._speed = 0.0        # in radians/s
        self._accel = 0.0        # speed increment /s
        self._tolerance = 0.0    # in radians
        self._motors_on = False
        self._lock_handler = None

    # Note: property decorators are great but don't allow child class to define
    #       just the setter...

    def get_torso_info(self):
        """Returns TorsoInfo instance"""
        return self._torso_info

    def get_neck_info(self):
        """Returns NeckInfo instance"""
        return self._neck_info

    def get_tolerance(self):
        """In radians"""
        return self._tolerance

    def set_tolerance(self, value):
        """In radians"""
        self._tolerance = value

    def set_lock_handler(self, handler):
        """function to call upon collision detection locking"""
        self._lock_handler = handler
    
    def switch_on(self, with_calibration=True):
        raise NotImplemented()

    def switch_off(self):
        raise NotImplemented()

    def unlock(self):
        """Unlock spine after collision detection cause locking"""
        raise NotImplemented()

    def set_neck_rot_pos(self, axis3_rot=None, axis3_pos=None):
        """Set head orientation and optional position from neck reference point.
        axis3_rot: triplet of floats in radians
        axis3_pos: triplet of floats in meters
        """
        # to be overriden
        raise NotImplemented()

    def set_torso_orientation(self, axis3):
        raise NotImplemented()

    def set_all(self, axis3_no, axis3_np, axis3_to):
        """Set orientation, position for neck and torso's orientation in one go.
        axis3_no: neck orientation (triplet of floats in radians)
        axis3_np: neck position (triplet of floats in meters)
        axis3_to: torso orientation
        """
        raise NotImplemented()


from spine.backend import SpineHW
SpineServer = SpineHW    
__all__ = ['Spine', 'TorsoInfo', 'NeckInfo', 'NotImplemented', 'SpineException']


if __name__ == '__main__':
    conf.name = sys.argv[-1]
    conf.load()
    try:
        server = comm.create_server(SpineServer, SpineClient, conf.conn_spine)
    except UserWarning, err:
        comm.LOG.error("FATAL ERROR: %s (%s)", sys.argv[0], err)
        exit(-1)
    server.serve_forever()
    LOG.debug("Spine server done")