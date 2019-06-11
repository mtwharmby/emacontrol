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
import socket


class Robot():

    def __init__(self):
        self.sample_index = None
        self.x_coord = None
        self.y_coord = None
        self.homed = False
        # TODO Need a connect method
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, message, wait_for=None):
        # FIXME This is a rough implementation; needs the wait_for stuff
        self.sock.send(message)

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


def power_off():
    """
    Disables power to the robot.
    """
    ema.send('powerOff')


def power_on():
    """
    Enables power to the robot.
    """
    ema.send('powerOn')


def reset():
    # TODO: Needs doc
    ema.send('reset')


def restart():
    # TODO: Needs doc
    ema.send('restartMotor')


def start():
    # TODO: Needs doc
    ema.send('start')


def stop():
    # TODO: Needs doc
    ema.send('stopMotor')


def unmount_sample():
    """
    Remove the sample currently on the diffractometer spinner and return it to
    its place in the sample magazine.

    The robot takes the following series of commands to do this:
    go to spinner -> close gripper on sample (move in and close) ->
    -> go to gate -> go to sample on board -> release sample
    """
    ema.send('spinner', wait_for='moveSpinner:done')
    ema.send('pick', wait_for='pickSample:done')
    ema.send('gate', wait_for='moveGate:done')
    ema.send('current', wait_for='returnCurrent:done')
    ema.send('release', wait_for='releaseSample:done')


ema = Robot()
