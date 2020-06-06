import os
import re

from collections import namedtuple

from emacontrol.network import SocketConnector
from emacontrol.utils import input_to_number, input_to_int, num_to_int

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

    def get_sample_number(self):
        # TODO Docstring
        coords = self.send('getSamPosOffset;')
        return Robot.xy_to_samplenr(Robot.parse_response(coords, ['X', 'Y']))

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

    def is_sample_mounted(self):
        # TODO Docstring
        mounted_resp = self.send('isSampleMounted;')
        mounted = mounted_resp.params[0]
        if mounted.lower() == 'yes':
            return True
        elif mounted.lower() == 'no':
            return False
        else:
            msg = 'Unknown sample mount state \'{}\''.format(mounted)
            raise RuntimeError(msg)

    def get_nearest_pos(self):
        pass

    def get_speed(self):
        # TODO Docstring
        speed_resp = self.send('getSpeed;')
        return speed_resp.params[0]

    def set_speed(self, speed_pc):
        # TODO Docstring
        msg = 'setSpeed:#{};'.format(speed_pc)
        self.send(msg, wait_for='setSpeed:done;')

    def is_powered(self):
        # TODO Docstring
        powered_resp = self.send('getPowerState;')
        powered = powered_resp.params[0]
        if powered.lower() == 'on':
            return True
        elif powered.lower() == 'off':
            return False
        else:
            msg = 'Unknown power state \'{}\''.format(powered)
            raise RuntimeError(msg)

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
    def xy_to_samplenr(xy):
        # TODO Docstring
        int_xy = {k: num_to_int(v) for k, v in xy.items()}
        return 10 * int_xy['x'] + int_xy['y'] + 1

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
        params = {}

        # Highly specific regex as we expect a well defined reponse from VAL3.
        # Anything else implies we have a problem.
        re_response = re.match(
            (r"(?P<cmd>[A-Za-z]*):(?:(?P<state>[A-Za-z]+)"
             + r"(?:_(?P<msg>[A-Za-z'\s!]+))?|(?P<params>#.*));"), message)

        if re_response:
            command = re_response.group('cmd')
            # A command name is always received. Additionally receive either a
            # state or a parameters list.
            if re_response.group('state'):
                state = re_response.group('state')

                if re_response.group('msg'):
                    # The state has a message associated with it (probably
                    # means something went wrong)
                    # - strip needed as string may be enclosed in single quotes
                    params['msg'] = re_response.group('msg').strip("\'")

            elif re_response.group('params'):
                # We have a list of parameters to process. This means the
                # command completed successfully (even if it doesn't send back
                # a state)
                state = 'ok'

                params_string = re_response.group('params')
                re_params_iter = re.finditer(
                    (r'#(?P<name>[A-Za-z]+|\d+)(?:(?=(?P<nums>[-0-9\.]+)|_'
                     + r'(?P<str>[A-Za-z]+))|.?)'),
                    params_string)

                for idx, par in enumerate(re_params_iter):
                    param_name = par.group('name')

                    if par.group('nums'):
                        # Numerical parameter value. Is it an int or a float?
                        try:
                            params[param_name] = input_to_int(
                                par.group('nums'))
                        except ValueError:
                            params[param_name] = float(par.group('nums'))

                    elif par.group('str'):
                        # String parameter value
                        # - strip needed as string may be enclosed in single
                        #   quotes
                        params[param_name] = par.group('str').strip("\'")

                    else:
                        # We only have the value of the parameter. Write it
                        # with its index.
                        try:
                            param_val = input_to_number(param_name)
                        except ValueError:
                            param_val = param_name
                        params[idx] = param_val
        else:
            msg = 'Unexpected message format: "{}"'.format(message)
            raise RuntimeError(msg)

        return Response(command, state, params)

    @staticmethod
    def parse_response(response, keys):
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
        return {key.lower(): response.params[key] for key in keys}


# namedtuple provides storage for a parsed responses from send method
Response = namedtuple('Response', ['command', 'state', 'params'])
