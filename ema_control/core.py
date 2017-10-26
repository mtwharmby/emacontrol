class Robot:
    def __init__(self):
        self.next_state(RobotReady)

    def next_state(self, state):
        self.__class__ = state
        self.do_state_change()

    def do_state_change(self):
        self.status=None
        raise NotImplementedError("No state change operation defined")

    def mount_sample(self):
        raise NotImplementedError("Cannot 'mount_sample' from status '%s'" % self.status)

    def unmount_sample(self):
        raise NotImplementedError("Cannot 'unmount_sample' from status '%s'" % self.status)


class RobotReady(Robot):
    def do_state_change(self):
        self.status = "Ready"

class RobotParked(Robot):
    pass