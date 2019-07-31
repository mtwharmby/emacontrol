import os

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
        self.sample_index = 1  # FIXME Should be reset to 1 by robot_end & robot_begin

    def _read_config(self):
        """
        Read the configuration for the socket from the configuration file given
        to the robot at initialisation. Currently only the hostname/IP address
        and the port are read from the config_file. See example_config.ini to
        see the structure of the config.
        """
        # TODO This should be made robot specific!
        super()._read_config()

    def send(self, message, wait_for=None):
        '''
        Send a message to the robot controller and wait for a response if
        needed

        Messages should correspond to commands in the comm module in the
        VAL3 code.

        Parameters
        ----------
        message : String message to send to the controller
        wait_for : String message to wait for the controller to send back
        '''
        recvd_msg = self.__send__(message)
        if (wait_for is not None) and (recvd_msg == wait_for):
            # Everything worked fine
            pass
        else:
            pass  # TODO Handle the situation - probably raise an exception

        return recvd_msg

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
        self.x_coord, self.y_coord = Robot.samplenr_to_xy(n)
        if verbose:
            print('Sample coords: ({}, {})'.format(self.x_coord, self.y_coord))
        self.send('setAxis:#X{0:d}#Y{1:d};'.format(self.x_coord, self.y_coord),
                  wait_for='setAxis:done;')

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