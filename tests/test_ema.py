
import os
import pytest
import sys

from mock import patch

from emacontrol.ema import Robot

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


def test_set_sample_coords():
    with patch('emacontrol.emaapi.Robot.send') as send_mock:
        ema = Robot()
        ema.set_sample_coords(75)
        send_mock.assert_called_with('setCoords:#X7#Y4;',
                                     wait_for='setCoords:done;')


# Method supports set_sample_coords
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

    with pytest.raises(ValueError, match=r".*greater than 0"):
        Robot.samplenr_to_xy(0)


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
    assert output == Response('powerOn', 'fail',
                              {0: 'RobotPowerCannotBeSwitched'})

    output = Robot.parse_message('getSAM:#X1.432#Y2.643#Z0.53;')
    assert output == Response('getSAM', '', {'X': 1.432, 'Y': 2.643,
                                             'Z': 0.53})
