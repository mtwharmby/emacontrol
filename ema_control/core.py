class Robot:

    def __init__(self):
        self.status = None
        self._next_state(RobotReady)
        self.has_sample = False
        self.sample_mounted = False

    def _next_state(self, state):
        self.__class__ = state
        self._do_state_change()

    def _do_state_change(self):
        raise NotImplementedError("No state change operation defined")

    def mount_sample(self):
        raise NotImplementedError("Cannot 'mount_sample' from status '%s'" % self.status)

    def unmount_sample(self):
        raise NotImplementedError("Cannot 'unmount_sample' from status '%s'" % self.status)


class RobotReady(Robot):

    def _do_state_change(self):
        self.status = "Ready"

    def mount_sample(self):
        self._next_state(RobotGetSample)


class RobotGetSample(Robot):

    def _do_state_change(self):
        self.status = "Picking sample"

    def mount_sample(self):
        self._next_state(RobotMoveSample)
        self.has_sample = True

    def unmount_sample(self):
        self._next_state(RobotMoveSample)
        self.has_sample = True
        self.sample_mounted = False


class RobotMoveSample(Robot):

    def _do_state_change(self):
        self.status = "Moving sample"

    def mount_sample(self):
        self._next_state(RobotParking)
        self.has_sample = False
        self.sample_mounted = True

    def unmount_sample(self):
        self._next_state(RobotParking)
        self.has_sample = False
        self.sample_mounted = False


class RobotParking(Robot):

    def _do_state_change(self):
        self.status = "Parking"

    def mount_sample(self):
        self._next_state(RobotParked)

    def unmount_sample(self):
        self._next_state(RobotReady)


class RobotParked(Robot):

    def _do_state_change(self):
        self.status = "Parked"

    def unmount_sample(self):
        self._next_state(RobotGetSample)
