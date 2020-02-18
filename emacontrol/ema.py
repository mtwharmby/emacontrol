import os
import re

from collections import namedtuple

from emacontrol.network import SocketConnector
from emacontrol.utils import input_to_int

# For Python >3.4, a more portable way to getting the home directory is:
# from pathlib import Path
# home_dir = Path.home()
# But pathlib doesn't seem to work on Debian 9. And this might not work under
# Windows...
default_config = os.path.join(os.path.expanduser('~'), '.robot.ini')


class Robot(SocketConnector):

    def __init__(self, config_file=default_config, robot_host=None,
                 robot_port=None, socket_timeout=60):
        super().__init__(robot_host, robot_port, config_file=config_file)
        self.sample_index = 1
        self.started = False

    def _read_config(self):
        """
        Read the configuration for the socket from the configuration file given
        to the robot at initialisation. Currently only the hostname/IP address
        and the port are read from the config_file. See example_config.ini to
        see the structure of the config.
        """
        # TODO This should be made robot specific!
        super()._read_config()

    def send(self, message, wait_for=None, parse=True):
        '''
        Send a message to the robot controller and wait for a response if
        needed

        Messages should correspond to commands in the comm module in the
        VAL3 code.

        Parameters
        ----------
        message : String
        Sent to the controller

        wait_for : String
        Message to wait for the controller to send back

        parse : boolean
        Should received message be run through message_parser to check for
        errors.
        '''
        recvd_msg = self.__send__(message)
        if parse:
            output = Robot.parse_message(recvd_msg)
        else:
            output = recvd_msg

        # We want to stop the robot in case of a fail unless explicitly told
        # not to with a wait for. Otherwise we don't know what the robot will
        # do next
        if ('fail' in recvd_msg) and (recvd_msg != wait_for):
            # TODO Log: 'Robot failed on message "{}" with: {}'.format(message,
            # output[state[0]])
            msg = 'Robot failed while running message "{}"'.format(message)
            raise RuntimeError(msg)
        if (wait_for is not None) and (recvd_msg != wait_for):
            # TODO Log: 'Robot response to "{}" was not as expected. Expected:
            # {}. Received: {}'.format(message, wait_for, recvd_msg)
            msg = 'Unexpected response from Robot: {}'.format(recvd_msg)
            raise RuntimeError(msg)

        return output

    def set_sample_number(self, n, verbose=False):
        """
        Sets the xy coordinates for the next sample to mount based on the index
        of that sample. Sends these coordinates to the robot controller.

        Parameters
        ----------
        n : integer
        Index of the sample to pick

        verbose : boolean
        If true prints the sample coordinates to screen
        """
        self.sample_index = n
        x_coord, y_coord = Robot.samplenr_to_xy(n)
        # TODO Log: 'Setting sample coordinates for sample {} to ({}, {})'
        # .format(n, x_coord, coord)
        if verbose:
            print('Sample position offset: ({}, {})'.format(x_coord, y_coord))
        self.send('setSamPosOffset:#X{0:d}#Y{1:d};'.format(x_coord, y_coord),
                  wait_for='setSamPosOffset:done;')

    def get_spin_position_offset(self):
        """
        Reads and returns the offset (trsf.{x,y,z} in VAL3) which has been
        applied to the SpinHomePosition to set the current currentSpinPosJ of
        the robot.

        Returns
        -------
        coords : tuple
        x, y, z offset in mm.
        """
        spin_offset = self.send('getSpinPosOffset;')
        return Robot._parse_state(spin_offset, ['X', 'Y', 'Z'])

    def set_spin_position_offset(self, spin_x, spin_y, spin_z, verbose=False):
        """
        Sends new x, y and z offsets to be applied to the SpinHomePosition of
        the robot to yield the new currentSpinPosJ. These values should be
        calculated from the goniometer head encoder positions.

        Parameters
        ----------
        spin_x, spin_y, spin_z : float
        New offsets in three dimensions for the spinner in mm
        """
        if verbose:
            print('Spinner coords: ({}, {}, {})'.format(spin_x, spin_y,
                                                        spin_z))
        self.send(('setSpinPosOffset:'
                   + '#X{0:.3f}#Y{1:.3f}#Z{2:.3f};'.format(spin_x, spin_y,
                                                           spin_z)),
                  wait_for='setSpinPosOffset:done;')

    def get_spin_home_position(self):
        """
        Reads the SpinHomePosition, i.e. the position where the robot was last
        calibrated against the goniometer head. This is the position which
        offsets are applied to.

        Returns
        -------
        spin_home_pos : dict
        A six-member dictionary containing the translations (3x in mm) and
        rotations (3x in degrees) of the spinner home position.
        """
        spin_home = self.send('getSpinHomePosition;')
        return Robot._parse_state(spin_home, ['X', 'Y', 'Z', 'RX', 'RY', 'RZ'])

    def get_spin_position(self):
        """
        Reads the current spinner position (i.e. SpinHomePosition + offset =
        currentSpinPosJ in VAL3). The returned values are absolute in the
        robot reference frame.

        Returns
        -------
        current_spin_pos : dict
        A six-member dictionary containing the translations (3x in mm) and
        rotations (3x in degrees) of the spinner position.
        """
        spin_pos = self.send('getSpinPosition;')
        return Robot._parse_state(spin_pos, ['X', 'Y', 'Z', 'RX', 'RY', 'RZ'])

    def get_gripper_coords(self):
        """
        Gets the current location of the gripper and returns the x, y, z
        coordinates.

        Returns
        -------
        coords : tuple
        x, y, z coordinates of the gripper in mm.
        """
        # FIXME If we can just return the gripper coords rather than the
        # spinner, we don't actually have to store the position of the gripper
        # as the "spinner position". We just have to move the gripper to the
        # right place.
        return self.get_spinner_coords()

    # def isPowered(self):
    #     power_state = self.send('getPowerState;')
    #     _, _, state = Robot.message_parser(power_state)
    #     if state.lower() == 'on':
    #         return True
    #     else:
    #         return False

    @staticmethod
    def samplenr_to_xy(n):
        """
        Convert the numerical index of the requested sample to xy coordinates
        on the sample magazine. Performs check that the input is an integer
        greater than zero.

        Parameters
        ----------
        n : integer (hopefully)

        Returns
        -------
        coordinates : tuple of integers
        x & y coordinates

        Raises
        ------
        ValueError : if n is not greater than 0
        """
        n = input_to_int(n)
        if n <= 0:
            raise ValueError('Expecting value greater than 0')
        # "Sample 1" is actually at position (0, 0). To make calculation
        # easier, subtract 1 (i.e. "Sample 1" = "Sample 0"). We use "Sample 1"
        # as this is easier to understand for users.
        n = n - 1
        coordinates = (n // 10, n % 10)
        return coordinates

    @staticmethod
    def parse_message(message):
        """
        Parse the messages that come from the robot.
        Messages have three formats:
        command:result;
        command:#parameters;
        command:result_'status';

        Parameters are separated out and passed into a dictionary, with the
        keys either the given names from the message or integers increasing
        from 0.

        Parameters
        ----------
        message : String
        Message to be parsed

        Returns
        -------
        response : namedtuple
        Response (command; result; status)
        """
        command, response = message.strip(';').split(':')
        result = ''
        state = {}

        # First handle the case we get some parameters back
        if response[0] == '#':
            param_parts = re.findall(
                r'(?P<chars>[A-Za-z]+)(?P<nums>[-0-9\.]*)',
                response
            )

            for idx, param in enumerate(param_parts):
                chars, nums = param

                # Are these named parameters? If so separate values and names
                if nums:
                    try:
                        state[chars] = input_to_int(nums)
                    except ValueError:
                        state[chars] = float(nums)
                else:
                    state[idx] = chars
        # Or is this just a string response?
        else:
            response = response.split('_')
            result = response[0]
            if len(response) == 2:
                state[0] = response[1].strip('\'')

        return Response(command, result, state)

    @staticmethod
    def _parse_state(response, keys):
        """
        Extracts only the requested keys from the state inside the given
        Response object. These are returned as a dictionary of lowercase keys
        and their values.

        Parameters
        ----------
        response : Response
        Object containing state to be extracted.

        keys : list
        String names of items to be returned

        Returns
        -------
        selected_keys : dict
        Dictionary with specified lowercase key names and their associated
        values.
        """
        return {key.lower(): response.state[key] for key in keys}


# namedtuple provides storage for a parsed responses from send method
Response = namedtuple('Response', ['command', 'result', 'state'])
