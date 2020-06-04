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
        assert ema.is_sample_mounted() is True
        send_mock.assert_called_with('isSampleMounted;')

        send_mock.return_value = 'isSampleMounted:#No;'
        assert ema.is_sample_mounted() is False


def test_is_sample_mounted_bad():
    with pytest.raises(RuntimeError, match=r"Unknown sample mount state.*"):
        with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
            ema = Robot()
            send_mock.return_value = 'isSampleMounted:#Dunno;'
            ema.is_sample_mounted()

def test_get_nearest_pos():
    raise NotImplementedError


def test_get_speed():
    raise NotImplementedError


def test_set_speed():
    raise NotImplementedError


def test_is_powered():
    with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
        ema = Robot()

        send_mock.return_value = 'getPowerState:#On;'
        assert ema.is_powered() is True
        send_mock.assert_called_with('getPowerState;')

        send_mock.return_value = 'getPowerState:#Off;'
        assert ema.is_powered() is False


def test_is_powered_bad():
    with pytest.raises(RuntimeError, match=r"Unknown power state.*"):
        with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
            ema = Robot()
            send_mock.return_value = 'getPowerState:#Bleep;'
            ema.is_powered()


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
    # TODO Add test of no match
    res = Robot.parse_message('getSamPosOffset:#X0    #Y0    ;')
    assert res == Response('getSamPosOffset', 'ok', {'X': 0, 'Y': 0})

    res = Robot.parse_message('setSamPos:done;')
    assert res == Response('setSamPos', 'done', {})

    res = Robot.parse_message('powerOff:done;')
    assert res == Response('powerOff', 'done', {})

    res = Robot.parse_message("powerOn:fail_'RobotPowerCannotBeSwitched';")
    assert res == Response('powerOn', 'fail',
                           {'msg': 'RobotPowerCannotBeSwitched'})

    res = Robot.parse_message('getPowerState:#On;')
    assert res == Response('getPowerState', 'ok', {0: 'On', })

    res = Robot.parse_message('getGripperState:open;')
    assert res == Response('getGripperState', 'open', {})
    # TODO Should be Reponse('getGripperState', 'ok', {0: 'open'})

    res = Robot.parse_message('getSpeed:#100;')
    assert res == Response('getSpeed', 'ok', {0: 100})
    # FIXME This breaks the regex
    # res = Robot.parse_message('getSpeed:#50.5;')
    # assert res == Response('getSpeed', 'ok', {0: 50.5})

    res = Robot.parse_message('isSampleMounted:#Yes;')
    assert res == Response('isSampleMounted', 'ok', {0: 'Yes'})
    res = Robot.parse_message('isSampleMounted:#No;')
    assert res == Response('isSampleMounted', 'ok', {0: 'No'})

    res = Robot.parse_message(('getSpinPosOffset:#X2.3  #Y4.2  #Z6.1  #RX0  '
                               + '#RY0  #RZ0  ;'))
    assert res == Response('getSpinPosOffset', 'ok',
                           {'X': 2.3, 'Y': 4.2, 'Z': 6.1, 'RX': 0, 'RY': 0,
                            'RZ': 0})

    res = Robot.parse_message(('getSpinPosition:#X984.71#Y397.23#Z-647.12'
                               + '#RX90#RY0#RZ90;'))
    assert res == Response('getSpinPosition', 'ok',
                           {'X': 984.71, 'Y': 397.23, 'Z': -647.12,
                            'RX': 90, 'RY': 0, 'RZ': 90})

    # This is from the command getNearestPosition; (!)
    res = Robot.parse_message(('getCurrentPosition:#DIST99.993'
                               + '#POS_currentSamPos;'))
    assert res == Response('getCurrentPosition', 'ok',
                           {'DIST': 99.993, 'POS': 'currentSamPos'})

    res = Robot.parse_message('getDiffOrigin:#X2#Y6#Z4;')
    assert res == Response('getDiffOrigin', 'ok', {'X': 2, 'Y': 6, 'Z': 4})

    # TODO Fix regex for this...
    # res = Robot.parse_message(":fail_'Unrecognised Command!';")
    # assert res == Response('', 'fail', {'msg': 'Unrecognised Command!'})

