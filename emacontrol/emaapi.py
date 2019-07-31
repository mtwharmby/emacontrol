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

from emacontrol.ema import Robot


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
