from ema_control.core import Robot, RobotParked

from nose.tools import assert_equal
from nose.tools import assert_false
from nose.tools import assert_true


class TestStateMachine:
    def setUp(self):
        self.robot = Robot()

    def test_initialise(self):
        """
        Robot should start in the READY state
        """
        assert_equal(self.robot.status, "Ready")

    def test_mount_sample_transitions(self):
        """
        Mount sample should have the following series of transitions:
        Ready -> Picking sample -> Moving sample -> Parking -> Parked
        Another call to mount_sample should throw an error
        """

        self.robot.mount_sample() #User trigger
        assert_equal(self.robot.status, "Picking sample")
        self.robot.mount_sample() #H/W trigger
        assert_equal(self.robot.status, "Moving sample")
        #Has sample = true
        self.robot.mount_sample() #H/W trigger
        assert_equal(self.robot.status, "Parking")
        #has_sample = false
        #sample_mounted = true
        self.robot.mount_sample() #H/W trigger
        assert_equal(self.robot.status, "Parked")

        try:
            self.robot.mount_sample()
            assert False, 'Should not be possible to call mount_sample in parked state'
        except(NotImplementedError):
            pass

    def test_unmount_sample_transitions(self):
        """
        Unmount sample should have the following transitions:
        Parked -> Recovering sample -> Moving sample -> Parking -> Ready
        Another call to unmount_sample should throw an error
        """

        #Set the initial state to Parked
        self.robot._next_state(RobotParked)

        self.robot.unmount_sample() #User trigger
        assert_equal(self.robot.status, "Picking sample")
        self.robot.unmount_sample() #H/W trigger
        assert_equal(self.robot.status, "Moving sample")
        self.robot.unmount_sample() #H/W trigger
        assert_equal(self.robot.status, "Parking")
        self.robot.unmount_sample() #H/W trigger
        assert_equal(self.robot.status, "Ready")

        try:
            self.robot.unmount_sample()
            assert False, 'Should not be possible to call unmount_sample in ready state'
        except(NotImplementedError):
            pass

    def test_sample_location_info(self):
        """
        Invariant:
        Ready - has_sample = 0; mounted_sample = 0
        Parked - has_sample = 0; mounted_sample = 1
        Moving - has_sample = 1; mounted_sample = 0

        Mount procedure:
        Get - has_sample = 0; mounted_sample = 0
        Parking - has_sample = 0; mounted_sample = 1

        Unmount procedure:
        Get - has_sample = 0; mounted_sample = 1
        Parking - has_sample = 0; mounted_sample = 0
        """

        #Ready
        assert_false(self.robot.has_sample)
        assert_false(self.robot.sample_mounted)

        #Get (mount)
        self.robot.mount_sample()
        assert_false(self.robot.has_sample)
        assert_false(self.robot.sample_mounted)

        #Moving
        self.robot.mount_sample()
        assert_true(self.robot.has_sample)
        assert_false(self.robot.sample_mounted)

        #Parking (mount)
        self.robot.mount_sample()
        assert_false(self.robot.has_sample)
        assert_true(self.robot.sample_mounted)

        #Parked
        self.robot.mount_sample()
        assert_false(self.robot.has_sample)
        assert_true(self.robot.sample_mounted)

        #Get (unmount)
        self.robot.unmount_sample()
        assert_false(self.robot.has_sample)
        assert_true(self.robot.sample_mounted)

        #Moving
        self.robot.unmount_sample()
        assert_true(self.robot.has_sample)
        assert_false(self.robot.sample_mounted)

        #Parking (mount)
        self.robot.unmount_sample()
        assert_false(self.robot.has_sample)
        assert_false(self.robot.sample_mounted)

        #Ready
        self.robot.unmount_sample()
        assert_false(self.robot.has_sample)
        assert_false(self.robot.sample_mounted)
