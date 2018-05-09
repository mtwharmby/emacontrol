import socket as sock

from emacontrol.core import Robot, RobotStatus


class EmaApi:
    def __init__(self):
        self.robot = Robot()

    def connect(self):
        pass

    # def set_X_axis(self, xVal):
    #     if xVal.isdigit():
    #         try:
    #             sock.send("defX")
    #             while sock.recv(16) != 'setXaxis:waiting':
    #                  print('... waiting for response ...')
    #             sock.send('%i' %int(defX))
    #         except:
    #             print('... socket error ...')
    #     else:
    #         print('... xVal is not a valid number ...')
    #
    # def set_Y_axis(self, yVal):
    #     if yVal.isdigit():
    #         try:
    #             sock.send("defY")
    #             while sock.recv(16) != 'setYaxis:waiting':
    #                  print('... waiting for response ...')
    #                  sock.send('%i' %int(defY))
    #         except:
    #             print('... socket error ...')
    #     else:
    #         print('... yVal is not a valid number ...')
    # def send_cmd(self, cmd):
    #     try:
    #         sock.send(cmd)

    def start(self):
        pass

    def stop(self):
        pass

    def pause(self):
        pass

    def mount_sample(self, n):
        #Assert that the robot is ready to go
        try:
            assert self.robot.status is RobotStatus.READY
        except AssertionError:
            print("Robot is not ready. Cannot mount a sample yet")

        #Set x and z axis locations
        self.robot.socket.send_config(...) #TODO

        self.robot.run()



    def mount_samples(self, mn):
        pass

    def unmount_sample(self):
        pass

    def clear_sample(self):
        pass

    def make_safe(self):
        pass
