import configparser
import os

import numpy as np

from collections import namedtuple

from emacontrol.emaapi import ema  # FIXME Move to __init__.py


# From ema.py  TODO Move to __init__.py
default_config = os.path.join(os.path.expanduser('~'), '.robot.ini')


class ConfigEditor():

    def __init__(self, config_file):
        """
        Helper for reading & writing to ConfigParser configs

        Parameters
        ----------
        config_file : String
        Path to ini style config file.
        """
        self.file = config_file
        self.config = configparser.ConfigParser()

    def _read_file(self):
        with open(self.file, 'r') as cfg_file:
            self.config.read_file(cfg_file)
            cfg_file.close()

    def get_position(self, pos_name):
        """
        Reads a position in the form x,y,z and return a CoordsXYZ

        Parameters
        ----------
        pos_name : String
        Name of key to read.

        Returns
        -------
        pos : CoordsXYZ
        Value of key.
        """
        self._read_file()
        pos = self.config['positions'][pos_name]
        return CoordsXYZ(*map(float, pos.split(',')))

    def set_position(self, pos_name, coords):
        """
        Set value of a position from a CoordsXYZ

        Parameters
        ----------
        pos_name : String
        Name of key to set.
        coords : CoordsXYZ
        Position to be written.
        """
        self._read_file()
        coords_s = ','.join(map(str, coords))
        if 'positions' in self.config.sections():
            self.config['positions'][pos_name] = coords_s
        else:
            self.config['positions'] = {pos_name: coords_s}
        with open(self.file, 'w') as cfg_file:
            self.config.write(cfg_file)


# FIXME Move to __init__.py
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

# Martin's original algorithm to calculate spinner position. It's wrong, but
# might be useful.
# spin_x = diffh + samx
# spin_y = diffv * np.cos(np.radians(-om)) + samy
# spin_z = diffv * np.sin(np.radians(-om)) + samz


def calibrate_spinner(samx, samy, samz, om, diffh, diffv, rotate_sense=1,
                      set_origin=False, set_spin_pos=False):
    """
    Calibrate the positions of the spinner and the diffractometer relative to
    one-another.

    The given diffractometer coordinates used to find the vector between
    diffractometer origin and the robot SpinnerHomePosition. This value is
    stored along with the absolute positions (in the robot coordinate system)
    of the diffractometer origin and the robot SpinnerHomePosition. The
    calibration values are used to calculate the offset which needs to be
    applied to the SpinnerHomePosition to move it to the goniometer head
    aligned to the beam. The update_spinner method is used to reset the
    current values of the offset to 0,0,0.

    If the old diffractometer origin is to be used after calibration, a check
    is made that the origin is still valid.

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
    set_spin_pos : bool
    Set the SpinnerHome position of the robot to the current position of the
    spinner.
    """
    # Calculate new vector between the goniometer 0 and the spinner position
    diffr_calib_xyz = diffr_pos_to_xyz(samx, samy, samz, om, diffh, diffv,
                                       rotate_sense=rotate_sense)
    ema_config.set_position('diffr_calib_xyz', diffr_calib_xyz)

    # Get and store the spinner position
    if set_spin_pos:
        raise NotImplementedError('Need SetSpinnerHome method')
    else:
        spin_position = ema.get_spin_position()
    spin_calib_xyz = CoordsXYZ(
        spin_position['x'],
        spin_position['y'],
        spin_position['z'])
    ema_config.set_position('spin_calib_xyz', spin_calib_xyz)

    # Calculate the diffractometer origin position in robot coordinates from
    # the two previously stored values
    diffr_robot_origin = CoordsXYZ(
        *np.subtract(spin_calib_xyz, diffr_calib_xyz)
    )
    # Diffractometer origin shouldn't change, so it doesn't have to be set
    # every time
    if set_origin:
        # After setting the origin, we don't want to run the origin check as
        # there's no point
        ema_config.set_position('diffr_robot_origin_xyz', diffr_robot_origin)
        run_checks = False
    else:
        # Check that the diffractometer origin is still the same and also
        # allow check of diffr_calib_xyz when updating spinner position
        robot_origin_xyz = ema_config.get_position('diffr_robot_origin_xyz')
        if not np.allclose(diffr_robot_origin, robot_origin_xyz, atol=0.02):
            raise RuntimeError('Unexpected change of diffractometer origin')

        run_checks = True

    # Supporting values have been updated. The new offset can be applied to
    # the robot SpinnerPosition
    update_spinner(samx, samy, samz, om, diffh, diffv,
                   rotate_sense=rotate_sense, run_checks=run_checks)


def update_spinner(samx, samy, samz, om, diffh, diffv, rotate_sense=1,
                   run_checks=True):
    """
    Given a set of diffractometer coordinates, calculates the offset necessary
    to align the robot SpinnerPosition with the goniometer head.

    The offset is calculated relative to the stored diffr_calib_xyz value. The
    validity of the stored value is checked by applying the calculated offset
    to the stored spin_calib_xyz position and then subtracting the diffr_xyz
    (calculated from the supplied diffractometer coordinates) to arrive at the
    diffractometer origin. This should be the same as the recorded value. If
    not, an error is thrown.

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

    if run_checks:
        # We check that diffr_calib_xyz is still valid for the offset we're
        # applying (i.e. the diffractometer origin has not changed)
        spin_calib_xyz = ema_config.get_position('spin_calib_xyz')
        spin_pos_xyz = np.add(diffr_offset, spin_calib_xyz)
        maybe_robot_origin = np.subtract(spin_pos_xyz, diffr_xyz)

        # The difference between the absolute spinner position and the current
        # diffr_xyz should be the same as the diffr_robot_origin_xyz. If it's
        # not, something has moved
        robot_origin_xyz = ema_config.get_position('diffr_robot_origin_xyz')

        origin_diff = maybe_robot_origin - robot_origin_xyz
        # Difference should be zero +/- 20 microns (half robot precision)
        if not np.allclose(origin_diff, np.array([0, 0, 0]), atol=0.02):
            raise RuntimeError(
                ('Requested spinner offset has different origin'
                 + ' to calibration by: {}'.format(origin_diff)))

    # We map robot & b/l coordinate systems on to one-another here:
    # z_rob <- x_bl; x_rob <- y_bl; y_rob <- z_bl
    ema.set_spin_position_offset(diffr_offset.z,
                                 diffr_offset.x,
                                 diffr_offset.y)
