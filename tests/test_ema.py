import os
import pytest
import sys

from mock import patch

from emacontrol.ema import Robot, Response

pathlib_path = False  # As this doesn't work with python < 3.6
if sys.version_info[0] >= 3:
    if sys.version_info[1] > 5:
        from pathlib import Path
        pathlib_path = True


def test_init():
    ema = Robot()
    assert ema.sample_index == 1
    assert ema.peer == (None, None)
    if pathlib_path:
        home_dir = Path.home()
    else:
        home_dir = os.path.expanduser('~')
    assert ema.config_file == os.path.join(home_dir, '.robot.ini')
    assert ema.sock is None
    assert ema.started is False


@patch.object(Robot, '__send__')
def test_send(send_mock):
    ema = Robot()

    # Normal behaviour
    send_mock.return_value = 'Command:done;'
    reply = ema.send('Command;', parse=False)
    assert reply == 'Command:done;'

    # Fails should throw an error...
    send_mock.return_value = 'Command:fail;'
    with pytest.raises(RuntimeError, match=r'.*failed.*'):
        reply = ema.send('Command;')

    # By explicitly expecting a fail, we can allow one to occur
    reply = ema.send('Command;', wait_for='Command:fail;', parse=False)
    assert reply == 'Command:fail;'

    # If we get a fail when we expected something else, it should still fail
    with pytest.raises(RuntimeError, match=r'.*failed.*'):
        reply = ema.send('Command;', wait_for='Command:done;', parse=False)

    send_mock.return_value = 'Command:squirrel;'
    # Likewise if we don't get what we expected
    with pytest.raises(RuntimeError, match=r'Unexpected.*'):
        reply = ema.send('Command;', wait_for='Command:done;', parse=False)


def test_get_sample_number():
    with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
        send_mock.return_value = (
            'getSamPosOffset:#X4    #Y6    ;'
        )  # This is raw output from the robot, hence __send__

        ema = Robot()
        res = ema.get_sample_number()

        send_mock.assert_called_with('getSamPosOffset;')
        assert res == 47


def test_set_sample_number():
    with patch('emacontrol.emaapi.Robot.send') as send_mock:
        ema = Robot()
        ema.set_sample_number(75)
        send_mock.assert_called_with('setSamPosOffset:#X7#Y4;',
                                     wait_for='setSamPosOffset:done;')


def test_is_sample_mounted():
    with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
        ema = Robot()

        send_mock.return_value = 'isSampleMounted:#Yes;'
        mounted = ema.is_sample_mounted()

        assert mounted is True
        send_mock.assert_called_with('isSampleMounted;')

        send_mock.return_value = 'isSampleMounted:#No;'
        mounted = ema.is_sample_mounted()

        assert mounted is False


def test_get_nearest_pos():
    raise NotImplementedError


def test_get_speed():
    raise NotImplementedError


def test_set_speed():
    raise NotImplementedError


def test_is_powered():
    raise NotImplementedError


###############################################################################
# Static Methods

# Method supports set_sample_number
def test_samplenr_to_xy():
    # Some specific examples of coords calculated...
    assert (0, 0) == Robot.samplenr_to_xy(1)
    assert (0, 1) == Robot.samplenr_to_xy(2)
    assert (1, 0) == Robot.samplenr_to_xy(11)

    # ...and all values for 300 samples
    n = 1
    for i in range(0, 30):
        for j in range(0, 10):
            assert (i, j) == Robot.samplenr_to_xy(n)
            n += 1


def test_samplenr_to_xy_bad_sample():
    # Sample position numbers start at 1. Number must be > 0
    with pytest.raises(ValueError, match=r".*greater than 0"):
        Robot.samplenr_to_xy(0)


def test_samplenr_to_xy_float():
    # Sample numbers are integers. This is to catch dodgy user input.
    with pytest.raises(ValueError, match=r".*integer.*"):
        Robot.samplenr_to_xy(3.2)


def test_xy_to_samplenr():
    assert 1 == Robot.xy_to_samplenr({'x': 0.0, 'y': 0.0})
    assert 43 == Robot.xy_to_samplenr({'x': 4, 'y': 2})
    assert 157 == Robot.xy_to_samplenr({'x': 15, 'y': 6})
    assert 264 == Robot.xy_to_samplenr({'x': 26, 'y': 3.0})


def test_xy_to_samplenr_float():
    # We should get an error if a float with a non-zero fraction
    with pytest.raises(ValueError, match=r".*integer.*"):
        Robot.xy_to_samplenr({'x': 3.4, 'y': 5.0})


# Method supports send
def test_parse_message():
    output = Robot.parse_message('setCoords:done;')
    assert output == Response('setCoords', 'done', {})

    output = Robot.parse_message('getPowerState:#On;')
    assert output == Response('getPowerState', '', {0: 'On', })

    output = Robot.parse_message('getCoords:#X4#Y2;')
    assert output == Response('getCoords', '', {'X': 4, 'Y': 2})

    msg = 'powerOn:fail_\'RobotPowerCannotBeSwitched\';'
    output = Robot.parse_message(msg)
    assert output == Response('powerOn',
                              'fail',
                              {0: 'RobotPowerCannotBeSwitched'})

    output = Robot.parse_message('getSAM:#X1.432#Y2.643#Z0.53;')
    assert output == Response('getSAM',
                              '',
                              {'X': 1.432, 'Y': 2.643, 'Z': 0.53})

    output = Robot.parse_message(('getSpinHomePosition:#X982#Y393#Z-653#RX90'
                                  + '#RY0#RZ0;'))
    assert output == Response('getSpinHomePosition',
                              '',
                              {'X': 982, 'Y': 393, 'Z': -653, 'RX': 90,
                               'RY': 0, 'RZ': 0})

def test_parse_response():
    raise NotImplementedError
