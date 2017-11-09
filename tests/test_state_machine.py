from emacontrol.core import Robot
from emacontrol.core import RobotParked
from emacontrol.core import UserCommands

from nose.tools import assert_equal
from nose.tools import assert_false
from nose.tools import assert_true


class TestStateMachine:
    def setUp(self):
        self.robot = Robot()

    def test_initialise(self):
        """
        Tests robot should initialises in the READY state with default variables
        """
        assert_equal(self.robot.status, "Ready")
        assert_false(self.robot._has_sample)
        assert_false(self.robot._sample_mounted)
        assert_equal(self.robot.command, UserCommands.NONE)

    def test_mount_sample_transitions(self):
        """
        Test transitions for the mount sample procedure

        Mount sample should have the following series of transitions:
        Ready -> Picking sample -> Moving sample -> Parking -> Parked
        Another call to mount_sample should throw an error
        """

        # Set the user command to mount sample
        self.robot.command = UserCommands.MOUNT_SAMPLE

        self.robot.run()  # User trigger
        assert_equal(self.robot.status, "Picking sample")

        self.robot.run()  # H/W trigger
        assert_equal(self.robot.status, "Moving sample")

        self.robot.run()  # H/W trigger
        assert_equal(self.robot.status, "Parking")

        self.robot.run()  # H/W trigger
        assert_equal(self.robot.status, "Parked")

        try:
            self.robot.run()
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
        self.robot._change_state(RobotParked)
        self.robot.command = UserCommands.UNMOUNT_SAMPLE

        self.robot.run()  # User trigger
        assert_equal(self.robot.status, "Picking sample")
        self.robot.run()  # H/W trigger
        assert_equal(self.robot.status, "Moving sample")
        self.robot.run()  # H/W trigger
        assert_equal(self.robot.status, "Parking")
        self.robot.run()  # H/W trigger
        assert_equal(self.robot.status, "Ready")

        try:
            self.robot.run()
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
        assert_false(self.robot._has_sample)
        assert_false(self.robot._sample_mounted)
        assert_equal(self.robot.command, UserCommands.NONE)

        #We're going to simulate the mounting procedure:
        self.robot.command = UserCommands.MOUNT_SAMPLE

        # Get (mount)
        self.robot.run()
        assert_false(self.robot._has_sample)
        assert_false(self.robot._sample_mounted)
        assert_equal(self.robot.command, UserCommands.MOUNT_SAMPLE)

        # Moving
        self.robot.run()
        assert_true(self.robot._has_sample)
        assert_false(self.robot._sample_mounted)
        assert_equal(self.robot.command, UserCommands.MOUNT_SAMPLE)

        # Parking (mount)
        self.robot.run()
        assert_false(self.robot._has_sample)
        assert_true(self.robot._sample_mounted)
        assert_equal(self.robot.command, UserCommands.MOUNT_SAMPLE)

        # Parked
        self.robot.run()
        assert_false(self.robot._has_sample)
        assert_true(self.robot._sample_mounted)
        assert_equal(self.robot.command, UserCommands.NONE)

        #Now we're going to simulate the unmounting procedure:
        self.robot.command = UserCommands.UNMOUNT_SAMPLE

        # Get (unmount)
        self.robot.run()
        assert_false(self.robot._has_sample)
        assert_true(self.robot._sample_mounted)
        assert_equal(self.robot.command, UserCommands.UNMOUNT_SAMPLE)

        # Moving
        self.robot.run()
        assert_true(self.robot._has_sample)
        assert_false(self.robot._sample_mounted)
        assert_equal(self.robot.command, UserCommands.UNMOUNT_SAMPLE)

        # Parking (mount)
        self.robot.run()
        assert_false(self.robot._has_sample)
        assert_false(self.robot._sample_mounted)
        assert_equal(self.robot.command, UserCommands.UNMOUNT_SAMPLE)

        # Ready
        self.robot.run()
        assert_false(self.robot._has_sample)
        assert_false(self.robot._sample_mounted)
        assert_equal(self.robot.command, UserCommands.NONE)
