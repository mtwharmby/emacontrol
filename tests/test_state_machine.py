from ema_control.core import Robot

from nose.tools import assert_equal


class TestStateMachine:
    def setUp(self):
        self.robot = Robot()

    def test_initialise(self):
        '''Robot should start in the READY state'''
        assert_equal(self.robot.state, "READY")
