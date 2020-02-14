import configparser
import os

import numpy as np

from collections import namedtuple


# From ema.py  TODO Move to __init__.py
default_config = os.path.join(os.path.expanduser('~'), '.robot.ini')


class ConfigEditor():
    def __init__(self, config_file):
        self.file = config_file
        self.config = configparser.ConfigParser()
        # self.config.sections()
        self.config.read(config_file)

    def get_position(self, pos_name):
        pos = self.config['positions'][pos_name]
        return CoordsXYZ(*map(float, pos.split(',')))

    def set_position(self, pos_name, coords):
        coords_s = ','.join(map(str, coords))
        self.config['positions'][pos_name] = coords_s
        with open(self.file, 'w') as cfg_file:
            self.config.write(cfg_file)


ema_config = ConfigEditor(default_config)


# Align diffractometer to beam and align robot to spinner
# Get spinner coords in diffractometer frame and calculate in xyz frame (spin_dxyz)
# Get gripper coordinates in xyz frame (grip_xyz)
# Calculate diffractometer 0 (in xyz frame) diff0_xyz = grip_xyz - spin_dxyz
# Specify offset of beam wrt to top of brass pin
# Calculate beam_xyz = grip_xyz + beam_offset
# Write diff0_xyz, beam_diff_offset and spin_dxyz to file

# beam_xyz - diff0_xyz (= beam_diff_offset) should be constant. This provides a check whether diff0 has moved.


# Align diffractometer to beam
# Get spinner coords in diffractometer frame and calculate in xyz frame (spin_dxyz)
# Calculate absolute postion of spinner from diff0_xyz: new_grip_xyz = diff0_xyz + spin_dxyz
# Check beam_diff_offset still consistent: ((spin_dxyz + diff0_xyz) + beam_offset) == beam_diff_offset

CoordsXYZ = namedtuple('CoordsXYZ', ['x', 'y', 'z'])


def diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv, rotate_sense=1):
    """
    Converts the diffractometer axis positions to xyz equivalents in mm.
    Results are rounded to the nearest micron.

    Parameters
    ----------
    samx : float
    Sample goniometer X axis position in mm
    samy : float
    Sample goniometer Y axis position in mm
    samz : float
    Sample goniometer Z axis position in mm
    om : float
    Sample omega axis position in degrees
    diffh : float
    Diffractometer horizontal axis position in mm
    diffv : float
    Diffractometer vertical axis position in mm
    rotate_sense : int
    Sense of rotation. Should have a value of 1 (clockwise) or -1 (counter-
    clockwise)

    Returns
    -------
    spinner_coords : tuple of ints
    The spinner cartesian coordinates as a tuple (shape (3,1)) in mm
    """
    spin_x = np.round(samx + diffh, 3)
    spin_y = np.round((samy * np.cos(np.radians((rotate_sense * -om)))
                       - samz * np.sin(np.radians((rotate_sense * -om)))
                       ) + diffv, 3)
    spin_z = np.round((samy * np.sin(np.radians((rotate_sense * -om)))
                       + samz * np.cos(np.radians((rotate_sense * -om)))
                       ), 3)

    return CoordsXYZ(spin_x, spin_y, spin_z)


def calibrate_spinner(samx, samy, samz, om, diffh, diffv, rotate_sense=1,
                      set_origin=False):
    """
    Calibrate the positions of the spinner and the diffractometer relative to
    one-another.

    The given diffractometer coordinates are used stored to be used
    subsequently to calculate the offset required to move the robot's
    SpinnerPosition to bring spinner and diffactometer into alignment if
    moved. The update_spinner function is used to reset the current spinner
    offset to 0,0,0.

    Parameters
    ----------
    samx : float
    Sample goniometer X axis position in mm
    samy : float
    Sample goniometer Y axis position in mm
    samz : float
    Sample goniometer Z axis position in mm
    om : float
    Sample omega axis position in degrees
    diffh : float
    Diffractometer horizontal axis position in mm
    diffv : float
    Diffractometer vertical axis position in mm
    rotate_sense : int
    Sense of rotation. Should have a value of 1 (clockwise) or -1 (counter-
    clockwise)
    set_origin : bool
    Write a new diffractometer origin to the config file.
    """
    diffr_calib_xyz = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv,
                                       rotate_sense=rotate_sense)
    ema_config.set_position('diffr_calib_xyz', diffr_calib_xyz)
    spin_position = ema.get_spin_position()
    spin_calib_xyz = CoordsXYZ(
        spin_position['x'],
        spin_position['y'],
        spin_position['z'])
    ema_config.set_position('spin_calib_xyz', spin_calib_xyz)

    diffr_robot_origin = CoordsXYZ(
        *np.subtract(spin_calib_xyz, diffr_calib_xyz)
    )
    if set_origin:
        ema_config.set_position('diffr_robot_origin', diffr_robot_origin)

    update_spinner(samx, samy, samz, om, diffh, diffv,
                   rotate_sense=rotate_sense)

def update_spinner(samx, samy, samz, om, diffh, diffv, rotate_sense=1):
    """
    Given a set of diffractometer coordinates, calculates the offset necessary
    to align the robot SpinnerPosition with the goniometer head.

    Offset is calculated relative to the stored diffr_calib_xyz value.

    Parameters
    ----------
    samx : float
    Sample goniometer X axis position in mm
    samy : float
    Sample goniometer Y axis position in mm
    samz : float
    Sample goniometer Z axis position in mm
    om : float
    Sample omega axis position in degrees
    diffh : float
    Diffractometer horizontal axis position in mm
    diffv : float
    Diffractometer vertical axis position in mm
    rotate_sense : int
    Sense of rotation. Should have a value of 1 (clockwise) or -1 (counter-
    clockwise)
    """
    diffr_xyz = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv,
                                 rotate_sense=rotate_sense)
    diffr_calib_xyz = ema_config.get_position('diffr_calib_xyz')
    diffr_offset = CoordsXYZ(*np.subtract(diffr_xyz, diffr_calib_xyz))

    ema.set_spin_position_offset(diffr_offset.x,
                                 diffr_offset.y,
                                 diffr_offset.z)
