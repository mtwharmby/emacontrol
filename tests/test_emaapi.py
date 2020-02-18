import pytest
from mock import call, patch

from emacontrol.emaapi import (robot_begin, robot_end, mount_sample,
                               unmount_sample, ema)
from emacontrol.ema import Response


# These tests are for the  basic start-up/shutdown methods
@patch('emacontrol.emaapi.ema.send')
def test_robot_begin(send_mock):
    assert ema.started is False
    # This is what we would get if we do a getSamPosOffset with the sample set
    # to 43
    getSamPosOffs_reply = Response('getSamPosOffset', '', {'X': 4, 'Y': 2})
    send_mock.return_value = getSamPosOffs_reply

    with patch('builtins.input'):
        robot_begin()
    send_calls = [call('getSamPosOffset;'),
                  call('powerOn;',
                       wait_for='powerOn:done;')]
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
                  call('moveSpinner;', wait_for='moveSpinner:done;'),
                  call('sampleRelease;', wait_for='sampleRelease:done;'),
                  call('moveOffside;', wait_for='moveOffside:done;')
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
    send_calls = [call('moveSpinner;', wait_for='moveSpinner:done;'),
                  call('samplePick;', wait_for='samplePick:done;'),
                  call('moveGate;', wait_for='moveGate:done;'),
                  call('moveSamPos;', wait_for='moveSamPos:done;'),
                  call('sampleRelease;', wait_for='sampleRelease:done;')
                  ]
    send_mock.assert_has_calls(send_calls)

    # And if we don't run robot begin:
    ema.started = False
    with pytest.raises(Exception, match=r".*Did you run the robot_begin.*"):
        unmount_sample()
