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

    def mount_sample(self):
        self.next_state(RobotGetSample)

class RobotGetSample(Robot):

    def do_state_change(self):
        self.status = "Picking sample"

    def mount_sample(self):
        self.next_state(RobotMoveSample)

    def unmount_sample(self):
        self.next_state(RobotMoveSample)

class RobotMoveSample(Robot):

    def do_state_change(self):
        self.status = "Moving sample"

    def mount_sample(self):
        self.next_state(RobotParking)

    def unmount_sample(self):
        self.next_state(RobotParking)

class RobotParking(Robot):

    def do_state_change(self):
        self.status = "Parking"

    def mount_sample(self):
        self.next_state(RobotParked)

    def unmount_sample(self):
        self.next_state(RobotReady)

class RobotParked(Robot):

    def do_state_change(self):
        self.status = "Parked"

    def unmount_sample(self):
        self.next_state(RobotGetSample)
