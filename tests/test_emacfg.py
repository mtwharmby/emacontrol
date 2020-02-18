import configparser
import os
import pytest

from mock import patch

import emacontrol.emacfg as emacfg
from emacontrol.emacfg import (CoordsXYZ, diffr_pos_to_xyz, update_spinner,
                               calibrate_spinner)


def test_diffr_pos_to_xyz():
    assert diffr_pos_to_xyz(0, 0, 0, 0, 0, 0) == (0.0, 0.0, 0.0)

    # @ om = 0: z along beam, x outboard (//diffh), y upward (// diffv)
    # om (assumed and defaulted to) clockwise when facing diffractometer
    samx = 4.0
    samy = 1.0
    samz = 2.0
    om = 0.0
    diffh = 3.0
    diffv = 5.0

    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(samx + diffh, samy + diffv, samz)

    om = 90.0  # x outboard (// diffh); y // -z0; z // y0 (//diffv);
    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(samx + diffh, samz + diffv, -samy)

    om = 180.0  # x outboard (// diffh); y // -y0; z // -z0
    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(samx + diffh, -samy + diffv, -samz)

    om = 270.0  # x outboard (// diffh); y // z0; z // -y0
    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(samx + diffh, -samz + diffv, samy)

    om = 120  # z slightly down and downstream; x up and downstream
    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(7.0, 6.232, -1.866)


def test_diffr_pos_to_xyz_CCW():
    # Same as test above, but now checking that the counterclockwise rotation
    # is correctly calculated.

    # @ om = 0: z along beam, x outboard (//diffh), y upward (// diffv)
    # om (assumed and defaulted to) clockwise when facing diffractometer.
    # Opposite sense of rotation used by setting the last argument,
    # rotate_sense, to -1
    samx = 4.0
    samy = 1.0
    samz = 2.0
    om = 0.0
    diffh = 3.0
    diffv = 5.0

    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv,
                           rotate_sense=-1)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(samx + diffh, samy + diffv, samz)

    om = 90.0  # x outboard (// diffh); y // -z0; z // y0 (//diffv);
    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv,
                           rotate_sense=-1)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(samx + diffh, -samz + diffv, samy)

    om = 180.0  # x outboard (// diffh); y // -y0; z // -z0
    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv,
                           rotate_sense=-1)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(samx + diffh, -samy + diffv, -samz)

    om = 270.0  # x outboard (// diffh); y // z0; z // -y0
    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv,
                           rotate_sense=-1)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(samx + diffh, samz + diffv, -samy)

    om = 120  # z slightly down and downstream; x up and downstream
    res = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv,
                           rotate_sense=-1)
    print('{}: {}'.format(om, res))
    assert res == CoordsXYZ(7.0, 2.768, -0.134)


@pytest.fixture
def robo_cfg():
    """
    Creates a default config file for use with all tests. This file can be
    updated using the update_robo_cfg function.
    """
    test_cfg = update_robo_cfg(
        'positions',
        kv_dict={
            'diffr_home': '7.0,6.232,-1.866',
            'diffr_calib_xyz': '0,0,0',
            'diffr_robot_origin_xyz': '22.47,50.322,76.5',
            'spin_calib_xyz': '22.47,50.322,76.5'
        },
        update=False
    )
    # N.B. By default the spin_calib_xyz and the diffr_calib_xyz are at the
    #      same position. This is because diffr_calib_xyz (i.e. the distance
    #      calculated from the goniometer coordinates) is 0.

    # Replace ema_config in emacfg for tests
    emacfg.ema_config = emacfg.ConfigEditor(test_cfg)

    return test_cfg


def update_robo_cfg(section, key=None, value=None, kv_dict=None, update=True):
    """
    Updates an existing robo_cfg file with either a key:value pair or a
    dictionary thereof
    """
    test_path = os.path.dirname(__file__)
    test_cfg = os.path.normpath(os.path.join(test_path, 'resources',
                                             'test_cfg.ini'))
    res_path = os.path.dirname(test_cfg)
    if not os.path.exists(res_path):
        os.makedirs(res_path)

    config = configparser.ConfigParser()
    # Existing config files need to be read first to update
    if update:
        config.read(test_cfg)

    if kv_dict:
        config[section] = kv_dict
    if key and value:
        config[section][key] = value

    with open(test_cfg, 'w') as test_cfg_fp:
        config.write(test_cfg_fp)

    return test_cfg


def assert_cfg_contains(cfg, section, key, value):
    """
    Test whether the given config file contains a section and key with the
    given value.
    """
    config = configparser.ConfigParser()
    config.read(cfg)
    assert config[section][key] == value


def test_get_config_position(robo_cfg):
    # Read a position value with the config editor
    assert (emacfg.ema_config.
            get_position('diffr_home') == CoordsXYZ(7.0, 6.232, -1.866)
            )


def test_set_config_position(robo_cfg):
    # Set a position value using the config editor
    pos = CoordsXYZ(1.1, 5, 3.3)
    emacfg.ema_config.set_position('squirrel', pos)

    config = configparser.ConfigParser()
    config.read(robo_cfg)
    assert_cfg_contains(robo_cfg, 'positions', 'squirrel', '1.1,5,3.3')


def test_calibrate_spinner(robo_cfg):
    samx = 2.0
    samy = 4.0
    samz = 1.0
    om = 0.0
    diffh = 5.0
    diffv = 3.0

    with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
        send_mock.side_effect = ([
            'getSpinPosition:#X29.47#Y57.322#Z77.5#RX0.841#RY89.653#RZ-0.064;',
            'setSpinPosOffset:done;',
        ])

        # Use the diffractometer coordinates and the provided spinner position
        # to determine a new diffractometer-robot calibration. Should update
        # the diffractometer-SpinnerPosition distance and the SpinnerPositions
        # only. As there's a new calibration, offset should be zero too.
        calibrate_spinner(samx, samy, samz, om, diffh, diffv)

        assert_cfg_contains(robo_cfg, 'positions',
                            'diffr_calib_xyz', '7.0,7.0,1.0')
        assert_cfg_contains(robo_cfg, 'positions',
                            'spin_calib_xyz', '29.47,57.322,77.5')
        send_mock.assert_called_with(
            'setSpinPosOffset:#X0.000#Y0.000#Z0.000;'
        )


def test_calibrate_spinner_origin_set(robo_cfg):
    # Do the same thing, but this time set the origin as well
    samx = 2.0
    samy = 4.0
    samz = 7.0
    om = 0.0
    diffh = 5.0
    diffv = 3.0

    with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
        send_mock.side_effect = ([
            'getSpinPosition:#X29.47#Y57.322#Z77.5#RX0.841#RY89.653#RZ-0.064;',
            'setSpinPosOffset:done;',
        ])

        calibrate_spinner(samx, samy, samz, om, diffh, diffv, set_origin=True)
        assert_cfg_contains(robo_cfg, 'positions',
                            'diffr_robot_origin_xyz', '22.47,50.322,70.5')


def test_update_spinner(robo_cfg):
    samx = 4.0
    samy = 1.0
    samz = 2.0
    om = 120.0
    diffh = 3.0
    diffv = 5.0

    with patch('emacontrol.emaapi.Robot.send') as send_mock:
        # Based on given diffractometer coords and the recorded
        # spinner/diffractometer positions, send an offset to the robot
        # SpinnerPosition.
        update_spinner(samx, samy, samz, om, diffh, diffv)
        send_mock.assert_called_with(
            'setSpinPosOffset:#X-1.866#Y7.000#Z6.232;',
            wait_for='setSpinPosOffset:done;'
        )

    # Try a non-zero distance between diffractometer origin and spinner:
    # Move the calibrated diffractometer position to 1.234,5.678,9.012
    # and update spin_calib_xyz by the same amount - otherwise errors!
    update_robo_cfg('positions',
                    key='diffr_calib_xyz',
                    value='1.234,5.678,9.012')
    update_robo_cfg('positions',
                    key='spin_calib_xyz',
                    value='23.704,56.0,85.512')

    with patch('emacontrol.emaapi.Robot.send') as send_mock:
        update_spinner(samx, samy, samz, om, diffh, diffv)
        send_mock.assert_called_with(
            'setSpinPosOffset:#X-10.878#Y5.766#Z0.554;',
            wait_for='setSpinPosOffset:done;'
        )


def test_origin_checking(robo_cfg):
    samx = 4.0
    samy = 1.0
    samz = 2.0
    om = 120.0
    diffh = 3.0
    diffv = 5.0

    # Move the calibrated diffractometer position to 1.234,5.678,9.012
    update_robo_cfg('positions',
                    key='diffr_calib_xyz',
                    value='1.234,5.678,9.012')

    with pytest.raises(RuntimeError, match=r".* different origin .*"):
        # Throws error an the spin_calib_xyz has not also been changed
        # --> diffr_calib_xyz is no longer valid
        update_spinner(samx, samy, samz, om, diffh, diffv)
