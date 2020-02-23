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
            'getSamPosOffset:#X4#Y6;'
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
        mounted = ema.get_sample_mounted()

        assert mounted is True
        send_mock.assert_called_with('isSampleMounted;')

        send_mock.return_value = 'isSampleMounted:#No;'
        mounted = ema.get_sample_mounted()

        assert mounted is False


def test_set_sample_mounted():
    with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
        ema = Robot()

        send_mock.return_value = 'sampleMounted:done;'
        ema.set_sample_mounted(True)
        send_mock.assert_called_with('sampleMounted;')

        send_mock.return_value = 'sampleUnmounted:done;'
        ema.set_sample_mounted(False)
        send_mock.assert_called_with('sampleUnmounted;')


def test_get_spin_position_offset():
    with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
        ema = Robot()
        send_mock.return_value = (
            'getSpinPosOffset:#X2.685#Y5.211#Z-8.646;'
        )  # This is raw output from the robot, hence __send__
        res = ema.get_spin_position_offset()
        assert res == {'x': 2.685, 'y': 5.211, 'z': -8.646}


def test_set_spin_position_offset():
    with patch('emacontrol.emaapi.Robot.send') as send_mock:
        ema = Robot()
        ema.set_spin_position_offset(7, 6, 2)
        send_mock.assert_called_with(('setSpinPosOffset:#X7.000#Y6.000'
                                      + '#Z2.000;'),
                                     wait_for='setSpinPosOffset:done;')


def test_get_spin_home_position():
    with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
        ema = Robot()
        send_mock.return_value = (
            'getSpinHomePosition:#X26.785#Y52.111#Z86.146#RX0.841#RY89.653'
            + '#RZ-0.064;'
        )  # This is raw output from the robot, hence __send__
        res = ema.get_spin_home_position()
        assert res == {'x': 26.785, 'y': 52.111, 'z': 86.146,
                       'rx': 0.841, 'ry': 89.653, 'rz': -0.064}


def test_get_spin_position():
    with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
        ema = Robot()
        send_mock.return_value = (
            'getSpinPosition:#X29.47#Y57.322#Z77.5#RX0.841#RY89.653#RZ-0.064;'
        )  # This is raw output from the robot, hence __send__
        res = ema.get_spin_position()
        assert res == {'x': 29.47, 'y': 57.322, 'z': 77.5,
                       'rx': 0.841, 'ry': 89.653, 'rz': -0.064}


def test_get_diffr_origin():
    with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
        send_mock.return_value = ('getDiffOrigin:#X22.47#Y50.322#Z70.5;')

        ema = Robot()
        res = ema.get_diffr_origin_calib()
        assert res == CoordsXYZ(22.47, 50.322, 70.5)


def test_get_diffr_pos_calib():
    with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
        send_mock.return_value = ('getDiffRel:#X7.0#Y6.232#Z-1.866;')

        ema = Robot()
        res = ema.get_diffr_pos_calib()
        assert res == CoordsXYZ(7.0, 6.232, -1.866)


# Method supports set_sample_number
def test_sample_to_coords():
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


def test_sample_to_coords_bad_sample():
    # Sample position numbers start at 1. Number must be > 0
    with pytest.raises(ValueError, match=r".*greater than 0"):
        Robot.samplenr_to_xy(0)


def test_sample_to_coords_float():
    # Sample numbers are integers. This is to catch dodgy user input.
    with pytest.raises(ValueError, match=r".*integer.*"):
        Robot.samplenr_to_xy(3.2)


def test_coords_to_sample():
    assert 1 == Robot.xy_to_samplenr({'x': 0.0, 'y': 0.0})
    assert 43 == Robot.xy_to_samplenr({'x': 4, 'y': 2})
    assert 157 == Robot.xy_to_samplenr({'x': 15, 'y': 6})
    assert 264 == Robot.xy_to_samplenr({'x': 26, 'y': 3.0})


def test_coords_to_sample_float():
    # We should get an error if a float with a non-zero fraction
    with pytest.raises(ValueError, match=r".*integer.*"):
        Robot.xy_to_samplenr({'x': 3.4, 'y': 5.0})


# Method supports send
def test_message_parser():
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
