import pytest
from mock import call, Mock, patch

from emacontrol.emaapi import (robot_begin, robot_end, mount_sample,
                               unmount_sample)


# These tests are for the  basic start-up/shutdown methods
@patch('emacontrol.emaapi.ema')
def test_robot_begin(ema_mock):
    with patch('builtins.input'):
        robot_begin()
    assert ema_mock.mock_calls == [call.send('powerOn;',
                                             wait_for='powerOn:done;')]


@patch('emacontrol.emaapi.ema')
def test_robot_end(ema_mock):
    robot_end()
    assert ema_mock.mock_calls == [call.send('powerOff;',
                                             wait_for='powerOff:done;')]


# The following tests are for functions which wait for a message to return from
# the robot before continuing
@patch('emacontrol.emaapi.ema')
def test_mount_sample(ema_mock):
    samcoords_mock = Mock()
    send_mock = Mock()
    ema_mock.connected = True
    ema_mock.set_sample_coords = samcoords_mock
    ema_mock.send = send_mock

    mount_sample(75,)
    # Preparation for mounting...
    samcoords_mock.assert_called_with(75, verbose=False)
    # ... and the actual process:
    send_calls = [call('next;', wait_for='moveNext:done;'),
                  call('pick;', wait_for='pickSample:done;'),
                  call('gate;', wait_for='moveGate:done;'),
                  call('spinner;', wait_for='moveSpinner:done;'),
                  call('release;', wait_for='releaseSample:done;'),
                  call('offside;', wait_for='moveOffside:done;')
                  ]
    send_mock.assert_has_calls(send_calls)

    ema_mock.connected = False
    with pytest.raises(Exception, match=r".*Did you run the robot_begin.*"):
        mount_sample(75)


@patch('emacontrol.emaapi.ema')
def test_unmount_sample(ema_mock):
    ema_mock.connected = True
    unmount_sample()
    send_calls = [call.send('spinner;', wait_for='moveSpinner:done;'),
                  call.send('pick;', wait_for='pickSample:done;'),
                  call.send('gate;', wait_for='moveGate:done;'),
                  call.send('current;', wait_for='returnCurrent:done;'),
                  call.send('release;', wait_for='releaseSample:done;')
                  ]
    ema_mock.assert_has_calls(send_calls)

    ema_mock.connected = False
    with pytest.raises(Exception, match=r".*Did you run the robot_begin.*"):
        unmount_sample()
