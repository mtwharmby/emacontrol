class Robot:
    def __init__(self):
        self.next_state(RobotReady)

    def next_state(self, state):
        self.__class__ = state
        self.do_state_change()

    def do_state_change(self):
        self.state=None
        raise NotImplementedError("No state change operation defined")

class RobotReady(Robot):
    def do_state_change(self):
        self.state = "READY"