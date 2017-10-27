from enum import Enum

class Robot:
    def __init__(self):
        self.status = None
        self._change_state(RobotReady)
        self.has_sample = False
        self.sample_mounted = False
        self.command = UserCommands.NONE

    def run(self):
        raise NotImplementedError("Cannot change status '{0}' with '{1}'".format(self.status, self.command._value_))

    def _change_state(self, state):
        self.__class__ = state
        self._do_state_change_action()

    def _do_state_change_action(self):
        raise NotImplementedError("No state change operation defined")


class RobotReady(Robot):
    def run(self):
        """
        Selects the state to change to based on the current value of
        self.command. If the current value is not found in the dictionary, the
        run method from the super-class is called instead (and raises error).
        """
        {UserCommands.MOUNT_SAMPLE : lambda: self._change_state(RobotGetSample)
         }.get(self.command, lambda: super(RobotReady, self).run())() # final () calls the lambda

    def _do_state_change_action(self):
        self.status = "Ready"


class RobotGetSample(Robot):
    def run(self):
        self._change_state(RobotMoveSample)

        # These values define how the sample position has changed in the new
        # state, so must be set after the state change. This goes for all
        # subsequent robot state classes.
        self.has_sample = True
        if self.command is UserCommands.UNMOUNT_SAMPLE:
            self.sample_mounted = False

    def _do_state_change_action(self):
        self.status = "Picking sample"


class RobotMoveSample(Robot):
    def run(self):
        self._change_state(RobotParking)

        self.has_sample = False
        # The sample mounted state needs to change as per the command.
        # But if the command is not mount or unmount, the behaviour is
        # undefined => error & call the super-class run method
        if self.command is UserCommands.MOUNT_SAMPLE:
            self.sample_mounted = True
        elif self.command is UserCommands.UNMOUNT_SAMPLE:
            self.sample_mounted = False
        else:
            pass  # super().run

    def _do_state_change_action(self):
        self.status = "Moving sample"


class RobotParking(Robot):
    def run(self):
        if self.command is UserCommands.MOUNT_SAMPLE:
            self._change_state(RobotParked)
        elif self.command is UserCommands.UNMOUNT_SAMPLE:
            self._change_state(RobotReady)
        else:
            super(RobotParking, self).run()
            pass
        self.command = UserCommands.NONE

    def _do_state_change_action(self):
        self.status = "Parking"


class RobotParked(Robot):
    def run(self):
        """
        Selects the state to change to based on the current value of
        self.command. If the current value is not found in the dictionary, the
        run method from the super-class is called instead (and raises error).
        """
        {UserCommands.UNMOUNT_SAMPLE : lambda: self._change_state(RobotGetSample)
         }.get(self.command, lambda: super(RobotParked, self).run())() # final () calls the lambda

    def _do_state_change_action(self):
        self.status = "Parked"


class UserCommands(Enum):
    NONE = "no command"
    MOUNT_SAMPLE = "mount sample"
    UNMOUNT_SAMPLE = "unmount sample"
