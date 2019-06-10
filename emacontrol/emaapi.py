from emacontrol.core import Robot, UserCommands


# Create an instance of the robot state machine so we can pass commands to it
robot = Robot("192.168.58.38", 10004)


def connect():
    '''
    Robot creates a process containing the state machine (if one doesn't
    already exist) and connects a socket.
    to talk to the real hardware.
    :return:
    '''
    pass


def disconnect(hard=False):
    '''
    Tell the robot to close the socket connection or kill the state machine
    process.
    :param hard: if True, kill state machine process too
    :return:
    '''
    pass


def reconnect(hard=False):
    '''
    Close an existing robot connection and connect again. If requested, kill
    the running state machine process.
    :param hard: if True, kill state machine process & restart
    :return:
    '''
    disconnect(hard)
    connect()


#These next two might not be neded. Could be included in the robot?
def init():
    '''
    Switch on power at the robot
    :return:
    '''
    robot.sock.power_on()


def halt():
    '''
    Switch off power to the robot
    :return:
    '''
    robot.sock.power_off()


def mount_sample(n):
    '''
    Tell the robot to mount a particular sample.
    :param n: The position number of the sample #TODO Needs a description from Mario
    :return:
    '''
    robot.set_position(n)
    robot.command = UserCommands.MOUNT_SAMPLE
    robot.go()


def unmount_sample():
    '''
    Take the current sample from the diffractometer and return it to its
    position in the magazines.
    :return:
    '''
    robot.command = UserCommands.UNMOUNT_SAMPLE
    robot.go()


def clear_sample():
    '''
    Move sample from diffractometer to the bin.
    :return:
    '''
    pass