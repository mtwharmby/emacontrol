import sys
import socket
import time
from PyTango import *


class EmaApi:
    def __init__(self):
        pass

    def connect(self):
        ip = "192.168.58.38"
        port = 10004
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((ip, port))
            print '... connection established ...'
            return sock
        except socket.error:
            print '... socket error ...'

    def set_X_axis(self, xVal):
        if xVal.isdigit():
            try:
                sock.send("defX")
                while sock.recv(16) != 'setXaxis:waiting':
                     print '... waiting for response ...'
                sock.send('%i' %int(defX))
            except:
                print '... socket error ...'#
        else:
            print '... xVal is not a valid number ...'

    def set_Y_axis(self, yVal):
        if yVal.isdigit():
            try:
                sock.send("defY")
                while sock.recv(16) != 'setYaxis:waiting':
                     print '... waiting for response ...'
                sock.send('%i' %int(defY))
            except:
                print '... socket error ...'
        else:
            print '... yVal is not a valid number ...'

    def send_cmd(self, cmd):
        try:
            sock.send(cmd)

    def start(self):
        pass

    def stop(self):
        pass

    def pause(self):
        pass

    def mount_sample(self, n):
        return self.mount_samples([n])

    def mount_samples(self, mn):
        pass

    def unmount_sample(self):
        pass

    def clear_sample(self):
        pass

    def make_safe(self):
        pass


class EmaException(Exception):
    """
    A base class for all custom exceptions that might be thrown from the EMA
    classes
    """
    def __init__(self, msg=None, *args):
        if msg is None:
            msg = "An error occurred executing EMA motion"
        super().__init__(msg, *args)