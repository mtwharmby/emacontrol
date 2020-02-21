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
    gotSamPos = ema.send('getSamPosOffset;')
    sam_pos = gotSamPos.state
    if sam_pos != {'X': 0, 'Y': 0}:  # FIXME Check flag; check powerstate
        sample = (sam_pos['X'] * 10) + sam_pos['Y'] + 1
        ema.sample_index = sample
        # TODO Log: 'Sample coords at robot start are ({}, {}) (Sample {}).
        # Should be (0, 0) for Sample 1'.format(coords['X'], coords['Y'],
        # sample)
        print('WARNING: Current sample is {} (not 1!).'.format(sample))
        print('Is there a sample on the spinner? '
              + 'Run \'unmount_sample()\' immediately if there is!')

    print('Starting E.M.A. sample changer... ', end='', flush=True)
    ema.send('powerOn;', wait_for='powerOn:done;')
    ema.started = True
    print('Done')


def robot_end():
    """
    Function to call at the end of a sample exchanging run. Turns power off to
    the robot and then closes the socket connection.
    """
    print('Powering off E.M.A. sample changer... ', end='', flush=True)
    ema.send('powerOff;', wait_for='powerOff:done;')
    ema.started = False
    # TODO If everything finished cleanly, samPosOffset should be set to 0
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
    if ema.started is False:
        msg = 'Robot not started. Did you run the robot_begin() method?'
        raise Exception(msg)
    ema.set_sample_number(n, verbose=verbose)
    # TODO Log: 'Mounting sample {}'
    print('Mounting sample {}... '.format(n), end='', flush=True)

    # Actually do the movements
    ema.send('moveSamPos;', wait_for='moveSamPos:done;')
    ema.send('samplePick;', wait_for='samplePick:done;')
    ema.send('moveGate;', wait_for='moveGate:done;')
    ema.send('moveSpinPos;', wait_for='moveSpinPos:done;')
    ema.send('sampleRelease;', wait_for='sampleRelease:done;')
    ema.send('moveParkPos;', wait_for='moveParkPos:done;')
    # TODO Log: 'Successfully mounted sample {}'
    print('Done')


def unmount_sample():
    """
    Remove the sample currently on the diffractometer spinner and return it to
    its place in the sample magazine.

    The robot takes the following series of commands to do this:
    go to spinner -> close gripper on sample (move in and close) ->
    -> go to gate -> go to sample on board -> release sample
    """
    if ema.started is False:
        msg = 'Robot not started. Did you run the robot_begin() method?'
        raise Exception(msg)
    # TODO Log: 'Unmounting sample {}'
    print('Unmounting sample... ', end='', flush=True)
    ema.send('moveSpinPos;', wait_for='moveSpinPos:done;')
    ema.send('samplePick;', wait_for='samplePick:done;')
    ema.send('moveGate;', wait_for='moveGate:done;')
    ema.send('moveSamPos;', wait_for='moveSamPos:done;')
    ema.send('sampleRelease;', wait_for='sampleRelease:done;')
    # TODO Log: 'Successfully Unmounted sample {}'
    print('Done')


ema = Robot()
