from emacontrol.core import RobotStateMachine, RobotStatus
from emacontrol.core import RobotStateMachineParked
from emacontrol.core import UserCommands

from nose.tools import assert_equal
from nose.tools import assert_false
from nose.tools import assert_true


class TestStateMachine:
    def setUp(self):
        self.robot_state_machine = RobotStateMachine()

    def test_initialise(self):
        """
        Tests robot should initialises in the READY state with default variables
        """
        assert_equal(self.robot_state_machine.status, RobotStatus.READY)
        assert_false(self.robot_state_machine._has_sample)
        assert_false(self.robot_state_machine._sample_mounted)
        assert_equal(self.robot_state_machine.command, UserCommands.NONE)

    def test_mount_sample_transitions(self):
        """
        Test transitions for the mount sample procedure

        Mount sample should have the following series of transitions:
        Ready -> Picking sample -> Moving sample -> Parking -> Parked
        Another call to mount_sample should throw an error
        """

        # Set the user command to mount sample
        self.robot_state_machine.command = UserCommands.MOUNT_SAMPLE

        self.robot_state_machine.run()  # User trigger
        assert_equal(self.robot_state_machine.status, RobotStatus.PICKING)

        self.robot_state_machine.run()  # H/W trigger
        assert_equal(self.robot_state_machine.status, RobotStatus.MOVING)

        self.robot_state_machine.run()  # H/W trigger
        assert_equal(self.robot_state_machine.status, RobotStatus.PARKING)

        self.robot_state_machine.run()  # H/W trigger
        assert_equal(self.robot_state_machine.status, RobotStatus.PARKED)

        try:
            self.robot_state_machine.run()
            assert False, 'Should not be possible to call mount_sample in parked state'
        except NotImplementedError:
            pass

    def test_unmount_sample_transitions(self):
        """
        Test transitions for the unmount sample procedure

        Unmount sample should have the following transitions:
        Parked -> Recovering sample -> Moving sample -> Parking -> Ready
        Another call to unmount_sample should throw an error
        """

        # Set the initial state to Parked & user command to unmount
        self.robot_state_machine._change_state(RobotStateMachineParked)
        self.robot_state_machine.command = UserCommands.UNMOUNT_SAMPLE

        self.robot_state_machine.run()  # User trigger
        assert_equal(self.robot_state_machine.status, RobotStatus.PICKING)
        self.robot_state_machine.run()  # H/W trigger
        assert_equal(self.robot_state_machine.status, RobotStatus.MOVING)
        self.robot_state_machine.run()  # H/W trigger
        assert_equal(self.robot_state_machine.status, RobotStatus.PARKING)
        self.robot_state_machine.run()  # H/W trigger
        assert_equal(self.robot_state_machine.status, RobotStatus.READY)

        try:
            self.robot_state_machine.run()
            assert False, 'Should not be possible to call unmount_sample in ready state'
        except NotImplementedError:
            pass

    def test_sample_location_info(self):
        """
        Tests for changes of has_sample, _sample_mounted and command variables
        
        Invariant:
        Ready - _has_sample = 0; _sample_mounted = 0
        Parked - _has_sample = 0; _sample_mounted = 1
        Moving - _has_sample = 1; _sample_mounted = 0

        Mount procedure:
        Get - _has_sample = 0; _sample_mounted = 0
        Parking - _has_sample = 0; _sample_mounted = 1

        Unmount procedure:
        Get - _has_sample = 0; _sample_mounted = 1
        Parking - _has_sample = 0; _sample_mounted = 0
        """

        # Ready
        assert_false(self.robot_state_machine._has_sample)
        assert_false(self.robot_state_machine._sample_mounted)
        assert_equal(self.robot_state_machine.command, UserCommands.NONE)

        #We're going to simulate the mounting procedure:
        self.robot_state_machine.command = UserCommands.MOUNT_SAMPLE

        # Get (mount)
        self.robot_state_machine.run()
        assert_false(self.robot_state_machine._has_sample)
        assert_false(self.robot_state_machine._sample_mounted)
        assert_equal(self.robot_state_machine.command, UserCommands.MOUNT_SAMPLE)

        # Moving
        self.robot_state_machine.run()
        assert_true(self.robot_state_machine._has_sample)
        assert_false(self.robot_state_machine._sample_mounted)
        assert_equal(self.robot_state_machine.command, UserCommands.MOUNT_SAMPLE)

        # Parking (mount)
        self.robot_state_machine.run()
        assert_false(self.robot_state_machine._has_sample)
        assert_true(self.robot_state_machine._sample_mounted)
        assert_equal(self.robot_state_machine.command, UserCommands.MOUNT_SAMPLE)

        # Parked
        self.robot_state_machine.run()
        assert_false(self.robot_state_machine._has_sample)
        assert_true(self.robot_state_machine._sample_mounted)
        assert_equal(self.robot_state_machine.command, UserCommands.NONE)

        #Now we're going to simulate the unmounting procedure:
        self.robot_state_machine.command = UserCommands.UNMOUNT_SAMPLE

        # Get (unmount)
        self.robot_state_machine.run()
        assert_false(self.robot_state_machine._has_sample)
        assert_true(self.robot_state_machine._sample_mounted)
        assert_equal(self.robot_state_machine.command, UserCommands.UNMOUNT_SAMPLE)

        # Moving
        self.robot_state_machine.run()
        assert_true(self.robot_state_machine._has_sample)
        assert_false(self.robot_state_machine._sample_mounted)
        assert_equal(self.robot_state_machine.command, UserCommands.UNMOUNT_SAMPLE)

        # Parking (mount)
        self.robot_state_machine.run()
        assert_false(self.robot_state_machine._has_sample)
        assert_false(self.robot_state_machine._sample_mounted)
        assert_equal(self.robot_state_machine.command, UserCommands.UNMOUNT_SAMPLE)

        # Ready
        self.robot_state_machine.run()
        assert_false(self.robot_state_machine._has_sample)
        assert_false(self.robot_state_machine._sample_mounted)
        assert_equal(self.robot_state_machine.command, UserCommands.NONE)
