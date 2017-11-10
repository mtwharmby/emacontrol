from enum import Enum

class Robot:
    def __init__(self):
        """
        Starts the Robot class in the Ready state and sets the sample booleans
        to indicate no sample is being handled. Command variable also set to
        no command.
        """
        self.status = None
        self._change_state(RobotReady)
        self._has_sample = False
        self._sample_mounted = False
        self.command = UserCommands.NONE

    def run(self):
        """
        Cause the state to change to a specified state by calling the
        _change_state method.

        :raises  NotImplementedError if state/command combination is not valid
        """
        raise NotImplementedError("Cannot change status '{0}' with '{1}'".format(self.status, self.command._value_))

    def _change_state(self, state):
        """
        Set the class of the current state to the new state, then call the
        _do_state_change_action method to effect the change.
        :param state: New state to change
        """
        self.__class__ = state
        self._do_state_change_action()

    def _do_state_change_action(self):
        """
        Method should set the status of Robot to a user readable value.
        Implementations of this method should include calls to the VAL3 code.

        :raises NotImplementedError: if there are no state change actions
        """
        raise NotImplementedError("No state change operation defined")


class RobotReady(Robot):
    """
    Robot is at the magazines and prepared to get the next sample. In this
    state the coordinates of the next sample should be set.

    @Mario - we should probably have some way to indicate the coordinates have
             been set, right?
    """
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
    """
    Robot has been given coordinates of a sample and moves to pick up that
    sample, but does not close the gripper arms.
    """
    def run(self):
        self._change_state(RobotMoveSample)

        # These values define how the sample position has changed in the new
        # state, so must be set after the state change. This goes for all
        # subsequent robot state classes.
        self._has_sample = True
        if self.command is UserCommands.UNMOUNT_SAMPLE:
            self._sample_mounted = False

    def _do_state_change_action(self):
        self.status = "Picking sample"


class RobotMoveSample(Robot):
    """
    Robot closes gripper arms on sample and moves sample from magazine to
    diffractometer or from diffractometer or magazine. Gripper arms do not
    release sample at end.
    """
    def run(self):
        self._change_state(RobotParking)

        self._has_sample = False
        # The sample mounted state needs to change as per the command.
        # But if the command is not mount or unmount, the behaviour is
        # undefined => error & call the super-class run method
        if self.command is UserCommands.MOUNT_SAMPLE:
            self._sample_mounted = True
        elif self.command is UserCommands.UNMOUNT_SAMPLE:
            self._sample_mounted = False
        else:
            pass  # super().run

    def _do_state_change_action(self):
        self.status = "Moving sample"


class RobotParking(Robot):
    """
    Robot gripper arms release sample and robot moves to the parking position
    (if mounting sample) or ready position (if unmounting sample).
    """
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
    """
    Robot has reached the parking position near the diffractometer and waits
    for an unmount instruction.
    """
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
    """
    List of commands with a user-readable string which can be accepted by the
    command variable of the state classes.
    """
    NONE = "no command"
    MOUNT_SAMPLE = "mount sample"
    UNMOUNT_SAMPLE = "unmount sample"
    STOP = "stop"
