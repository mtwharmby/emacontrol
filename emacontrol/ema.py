import os
import numpy as np
import re

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
        message : String message to send to the controller
        wait_for : String message to wait for the controller to send back
        parse : Bool should received message be run through message_parser to
                     check for errors
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

    def set_sample_coords(self, n, verbose=False):
        """
        Sets the xy coordinates for the next sample to mount based on the index
        of that sample. Sends these coordinates to the robot controller.

        Parameters
        ----------
        n : integer index of the sample to pick
        verbose : boolean if true prints the sample coordinates to screen
        """
        self.sample_index = n
        x_coord, y_coord = Robot.samplenr_to_xy(n)
        # TODO Log: 'Setting sample coordinates for sample {} to ({}, {})'
        # .format(n, x_coord, coord)
        if verbose:
            print('Sample coords: ({}, {})'.format(x_coord, y_coord))
        self.send('setCoords:#X{0:d}#Y{1:d};'.format(x_coord, y_coord),
                  wait_for='setCoords:done;')

    def get_spinner_coords(self):
        # TODO Add docstring!
        spin_coords = self.send('getSpinnerCoords;')
        _, state, _ = Robot.parse_message(spin_coords)
        # TODO Finish me!

    def set_spinner_coords(self, samx, samy, samz, om, diffh, diffv,
                           verbose=False):
        # TODO Add docstring!
        spinner_coords = Robot._vector_calc(samx, samy, samz, om, diffh, diffv)
        if verbose:
            print('Spinner coords: ({}, {}, {})'.format(*spinner_coords))
        self.send(('setSpinnerCoords:'
                   + '#X{0:.5f}#Y{1:.5f}#Z{2:.5f};'.format(*spinner_coords)),
                  wait_for='setSpinnerCoords:done;')

    # def isPowered(self):
    #     power_state = self.send('getPowerState;')
    #     _, state, _ = Robot.message_parser(power_state)
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
        tuple of integers : x & y coordinates

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
        command:result_status';

        Parameters are separated out with either given names or increasing
        integers and passed into a dictionary.

        Parameters
        ----------
        message : String to parse

        Returns
        -------
        dict containing three fields (command; result; status)
        """
        command, response = message.strip(';').split(':')
        result = ''
        state = {}

        # First handle the case we get some parameters back
        if response[0] == '#':
            parameters = re.findall(r'[A-Za-z]+\d*\.*\d*', response)
            for i in range(len(parameters)):
                chars = re.search(r'[A-Za-z]+', parameters[i]).group()
                nums = re.search(r'\d+\.*\d*', parameters[i])

                # Are these named parameters? If so separate values and names
                if nums:
                    try:
                        state[chars] = input_to_int(nums.group())
                    except ValueError:
                        state[chars] = float(nums.group())
                else:
                    state[i] = chars
        # Or is this just a string response?
        else:
            response = response.split('_')
            result = response[0]
            if len(response) == 2:
                state[0] = response[1].strip('\'')

        return {'command': command, 'result': result, 'state': state}

    @staticmethod
    def _vector_calc(samx, samy, samz, om, diffh, diffv):
        # TODO Add docstring!
        # TODO Should this already calc position based on known position?
        spin_x = diffh + samx
        spin_y = diffv * np.cos(np.radians(-om)) + samy
        spin_z = diffv * np.sin(np.radians(-om)) + samz

        return (spin_x, spin_y, spin_z)
