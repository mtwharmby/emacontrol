from ema_control.core import Robot, RobotParked

from nose.tools import assert_equal


class TestStateMachine:
    def setUp(self):
        self.robot = Robot()

    def test_initialise(self):
        '''Robot should start in the READY state'''
        assert_equal(self.robot.status, "Ready")

    def test_mount_sample_transitions(self):
        '''Mount sample should have the following series of transitions:
        Ready -> Picking sample -> Moving sample -> Parking -> Parked
        Another call to mount_sample should throw an error'''

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

    def test_unmount_sample_transitions(self):
        '''Unmount sample should have the following transitions:
        Parked -> Recovering sample -> Moving sample -> Parking -> Ready
        Another call to unmount_sample should throw an error'''

        #Set the initial state to Parked
        self.robot.next_state(RobotParked)

        self.robot.unmount_sample() #User trigger
        assert_equal(self.robot.status, "Recovering sample")
        self.robot.unmount_sample() #H/W trigger
        assert_equal(self.robot.status, "Moving sample")
        self.robot.unmount_sample() #H/W trigger
        assert_equal(self.robot.status, "Parking")
        self.robot.unmount_sample() #H/W trigger
        assert_equal(self.robot.status, "Ready")

        #Need to test location of sample before making some (all?) transitions
