"""
Robot class should create a socket and provide methods to use that socket to pass instructions through that socket to the robot.
Methods on the module should then use an instance of this class to send commands to achieve tasks

methods required:
X power_on
X power_off
X start
X stop
- set_axis
- homing
- power_status
- mount_sample
- unmount_sample
- (status)
- (calibrate_sam)
- (compare_sam)
"""
import configparser
import os
import time
import socket

# For Python >3.4, a more portable way to getting the home directory is:
# from pathlib import Path
# home_dir = Path.home()
# This doesn't seem to work on Debian 9. This might not work under Windows...
default_config = os.path.join(os.path.expanduser('~'), '.robot.ini')


class Robot():

    def __init__(self, config_file=default_config):
        self.sample_index = None
        self.x_coord = None
        self.y_coord = None
        self.homed = False
        self.connected = False
        self.sock = None
        self.address = None
        self.port = None
        self.config_file = config_file

    def __read_config__(self):
        if not os.path.exists(self.config_file):
            raise(FileNotFoundError('Cannot find E.M.A. API config file: {}'
                                    .format(self.config_file)))
        confparse = configparser.ConfigParser()
        confparse.read(self.config_file)

        # Read values from config ensuring port is integer > 0
        self.address = confparse.get('robot', 'address')
        self.port = __input_to_int__(confparse.get('robot', 'port'))
        if self.port <= 0:
            raise ValueError('Expecting value greater than 0')

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if (self.address is None) or (self.port is None):
            self.__read_config__()
        self.sock.connect((self.address, self.port))
        self.connected = True

    def disconnect(self):
        self.sock.close()
        self.connected = False

    def send(self, message, wait_for=None):
        self.sock.send(message.encode())
        if wait_for:
            msg_len = len(wait_for.encode())
            recv_msg = ''

            while recv_msg != wait_for.encode():
                recv_msg = self.sock.recv(msg_len)

    def set_homed(self):
        print("Robot is not homed. Performing homing procedure...")
        self.send('gate', wait_for='moveGate:done')
        self.send('homing', wait_for='homing:done')
        self.homed = True

    def set_sample_coords(self, n):
        """
        Sets the xy coordinates for the next sample to mount based on the index
        of that sample. Sends these coordinates to the robot controller.

        Parameters
        ----------
        n : integer index of the sample to pick
        """
        self.sample_index = n
        self.x_coord, self.y_coord = Robot.samplenr_to_xy(n) 
        self.send('setAxis#X{0:d}#Y{1:d}'.format(self.x_coord, self.y_coord),
                  wait_for='setAxis:done')

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
        # In the original code this was expressed as:
        # x=((n-1)/10)+1
        # y=((n-1)%10)+1
        n = __input_to_int__(n)
        if n <= 0:
            raise ValueError('Expecting value greater than 0')
        return (n // 10 + 1, n % 10)


def __input_to_int__(value):
    """
    Checks that user input is an integer.

    Parameters
    ----------
    n : user input to check

    Returns
    -------
    integer : n cast to an integer

    Raises
    ------
    ValueError : if n is not an integer
    """
    if str(value).isdigit():
        return int(value)
    else:
        raise ValueError('Expecting integer. Got: "{0}" ({1})'
                         .format(value, type(value)))


def mount_sample(n):
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
        raise Exception('Robot not connected. Did you run the start() method?')
    ema.set_sample_coords(n)
    if not ema.homed:
        ema.set_homed()

    # Actually do the movements
    ema.send('next', wait_for='moveNext:done')
    ema.send('pick', wait_for='pickSample:done')
    ema.send('gate', wait_for='moveGate:done')
    ema.send('spinner', wait_for='moveSpinner:done')
    ema.send('release', wait_for='releaseSample:done')
    ema.send('offside', wait_for='moveOffside:done')


def start():
    """
    Prepare the robot for a sample exchanging run. Opens the socket connection
    and then turns the power on to the robot.
    """
    ema.connect()
    ema.send('powerOn')
    time.sleep(3)  # I don't know if there's a return on this call. So we wait. 


def stop():
    """
    Function to call at the end of a sample exchanging run. Turns power off to
    the robot and then closes the socket connection.
    """
    ema.send('powerOff')
    ema.disconnect()


def unmount_sample():
    """
    Remove the sample currently on the diffractometer spinner and return it to
    its place in the sample magazine.

    The robot takes the following series of commands to do this:
    go to spinner -> close gripper on sample (move in and close) ->
    -> go to gate -> go to sample on board -> release sample
    """
    if not ema.connected:
        raise Exception('Robot not connected. Did you run the start() method?')
    ema.send('spinner', wait_for='moveSpinner:done')
    ema.send('pick', wait_for='pickSample:done')
    ema.send('gate', wait_for='moveGate:done')
    ema.send('current', wait_for='returnCurrent:done')
    ema.send('release', wait_for='releaseSample:done')


ema = Robot()
