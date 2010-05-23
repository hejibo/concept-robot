
import logging

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)


class ConflictSolver(object):
    def __init__(self):
        self.AUs = {}

    def set_available_AUs(self, available_AUs):
        """Define list of AUs available for a specific face.
         available_AUs: list of AU names.
        """
        for name in available_AUs:
            self.AUs[name] = [0]*4  # target_val, duration, elapsed, value
        LOG.info("Available AUs: %s" % sorted(self.AUs.keys()))

    def set_AU(self, origin, name, target_value, duration):
        """Set targets for a specific AU, giving priority so specific inputs.
         origin: name of the input
         name: AU name
         target_value: normalized value
         duration: time in 
        """
        try:
            self.AUs[name][:3] = target_value, duration, 0
        except KeyError:
            if len(name) != 2:
                raise Exception('AU %s is not defined' % name)
            self.AUs[name+'R'][:3] = target_value, duration, 0
            self.AUs[name+'L'][:3] = target_value, duration, 0
            LOG.debug("set AU[%sR/L]: %s" % (name, self.AUs[name+'R']))
        else:
            LOG.debug("set AU[%s]: %s" % (name, self.AUs[name]))

    def update(self, time_step):
        """Update AU values."""
        if self.blink_p > random.random():
            self.do_blink(BLINK_DURATION)
        #TODO: use motion dynamics
        for id,info in self.AUs.iteritems():
            target, duration, elapsed, val = info
            if val == target or elapsed > duration:
                continue        # let self.AUs[id] be reset on next command

            factor = not duration and 1 or elapsed/duration
            self.AUs[id][2:] = elapsed+time_step, val + (target - val)*factor

