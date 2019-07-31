"""
Robot class should create a socket and provide methods to use that socket to
pass instructions through that socket to the robot. Methods on the module
should then use an instance of this class to send commands to achieve tasks.

    TODO
    - When does the homing procedure actually need to be run?
    - Add recording of last mounted sample
    - Add recording of last message sent
    - Add state machine to allow recovery if software crashes

    NEEDED
    Clear sample(?)
    Go to zero position (check with Mario what is best)
    Setting of sam postion
"""
# TODO Add logging!

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


def robot_begin():
    """
    Prepare the robot for a sample exchanging run. Opens the socket connection
    and then turns the power on to the robot.
    """
    # TODO Ideally this would check the interlock programmatically. But this
    # isn't an option yet.
    input('Have you pressed the reset button?\nPress enter to continue...')
    print('Starting E.M.A. sample changer... ', end='', flush=True)
    ema.send('powerOn;', wait_for='powerOn:done;')
    print('Done')


def robot_end():
    """
    Function to call at the end of a sample exchanging run. Turns power off to
    the robot and then closes the socket connection.
    """
    print('Powering off E.M.A. sample changer... ', end='', flush=True)
    ema.send('powerOff;', wait_for='powerOff:done;')
    print('Done')


def mount_sample(n, verbose=False):
    """
    Mount a sample with the requested index on the sample spinner.

    The robot takes the following series of commands to do this:
    go to sample on board-> close gripper on sample (move down and close) ->
    -> go to gate -> go to spinner -> release sample ->
    -> go to offside position

    Parameters
    ----------
    n : integer index of the sample to be mounted
    """
    if not ema.connected:
        msg = 'Robot not connected. Did you run the robot_begin() method?'
        raise Exception(msg)
    ema.set_sample_coords(n, verbose=verbose)
    print('Mounting sample {}... '.format(n), end='', flush=True)

    # Actually do the movements
    ema.send('next;', wait_for='moveNext:done;')
    ema.send('pick;', wait_for='pickSample:done;')
    ema.send('gate;', wait_for='moveGate:done;')
    ema.send('spinner;', wait_for='moveSpinner:done;')
    ema.send('release;', wait_for='releaseSample:done;')
    ema.send('offside;', wait_for='moveOffside:done;')
    print('Done')


def unmount_sample():
    """
    Remove the sample currently on the diffractometer spinner and return it to
    its place in the sample magazine.

    The robot takes the following series of commands to do this:
    go to spinner -> close gripper on sample (move in and close) ->
    -> go to gate -> go to sample on board -> release sample
    """
    if not ema.connected:
        msg = 'Robot not connected. Did you run the robot_begin() method?'
        raise Exception(msg)
    print('Unmounting sample... ', end='', flush=True)
    ema.send('spinner;', wait_for='moveSpinner:done;')
    ema.send('pick;', wait_for='pickSample:done;')
    ema.send('gate;', wait_for='moveGate:done;')
    ema.send('current;', wait_for='returnCurrent:done;')
    ema.send('release;', wait_for='releaseSample:done;')
    print('Done')


ema = Robot()
