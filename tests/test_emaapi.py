import pytest
from mock import call, patch

from emacontrol.emaapi import (robot_begin, robot_end, mount_sample,
                               unmount_sample, ema)


# These tests are for the  basic start-up/shutdown methods
# FIXME Re-write this test
def test_robot_begin():
    with patch('emacontrol.emaapi.ema.__send__') as send_mock:
        assert ema.started is False
        # This is what we would get if we do a getSamPosOffset with the sample
        # set to 43
        send_mock.side_effect = ['getSamPosOffset:#X4    #Y2    ;',
                                 'powerOn:done;']

        with patch('builtins.input'):
            robot_begin()

        send_calls = [call('getSamPosOffset;'),
                      call('powerOn;')]  # TODO Needs wait_for check here
        send_mock.assert_has_calls(send_calls)

    assert ema.started is True


@patch('emacontrol.emaapi.ema.send')
def test_robot_end(ema_mock):
    ema.started = True
    robot_end()
    assert ema_mock.mock_calls == [call('powerOff;',
                                        wait_for='powerOff:done;')]
    assert ema.started is False


# The following tests are for functions which wait for a message to return from
# the robot before continuing
@patch('emacontrol.emaapi.ema.send')
@patch('emacontrol.emaapi.ema.set_sample_number')
def test_mount_sample(sample_num_mock, send_mock):
    # Mount a sample. This should set the coordinates and then do the mount
    ema.started = True
    mount_sample(75,)

    sample_num_mock.assert_called_with(75, verbose=False)
    send_calls = [call('moveSamPos;', wait_for='moveSamPos:done;'),
                  call('samplePick;', wait_for='samplePick:done;'),
                  call('moveGate;', wait_for='moveGate:done;'),
                  call('moveSpinPos;', wait_for='moveSpinPos:done;'),
                  call('sampleRelease;', wait_for='sampleRelease:done;'),
                #   call('sampleMounted;', wait_for='sampleMounted:done;'),
                  call('moveParkPos;', wait_for='moveParkPos:done;')
                  ]
    send_mock.assert_has_calls(send_calls)

    # And if we don't run robot begin:
    ema.started = False
    with pytest.raises(Exception, match=r".*Did you run the robot_begin.*"):
        mount_sample(75)


@patch('emacontrol.emaapi.ema.send')
def test_unmount_sample(send_mock):
    # Unmount the sample. Just takes the current sample back to its old
    # position in the magazine
    ema.started = True
    unmount_sample()
    send_calls = [call('moveSpinPos;', wait_for='moveSpinPos:done;'),
                  call('samplePick;', wait_for='samplePick:done;'),
                #   call('sampleUnmounted;', wait_for='sampleUnmounted:done;')
                  call('moveGate;', wait_for='moveGate:done;'),
                  call('moveSamPos;', wait_for='moveSamPos:done;'),
                  call('sampleRelease;', wait_for='sampleRelease:done;')
                  ]
    send_mock.assert_has_calls(send_calls)

    # And if we don't run robot begin:
    ema.started = False
    with pytest.raises(Exception, match=r".*Did you run the robot_begin.*"):
        unmount_sample()
