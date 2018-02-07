import socket
import time
from emacontrol.emaapi import EmaException


class RobotSocket:
    def __init__(self, address, port):
        """
        Creates a socket configured with an address and port to communicate
        with the VAL3 robot code
        :param address: IP address or DNS name where the VAL3 server is
        :param port: port number on VAL3 server to connect to
        """
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((address, port))

    def send_cmd(self, cmd, await=None, timeout=10):
        """
        Send a command to the robot. If a reponse is required, this can also be
        specified. It is usually expected commands will complete within 10
        seconds, but this can be changed by specifying a value for timeout.
        :param cmd: Command to be performed
        :param await:  Expected reply from VAL3
        :param timeout: Time to wait before throwing an error
        :return:
        """
        self.socket.send(cmd)
        if await:
            while self.socket.recv(16) != await:
                time.sleep(1)
                timeout -= 1
                if timeout <= 0:
                    raise CommunicationException("Timed out waiting for response '{}' from '{}:{}".format(await, self.address, self.port))


class CommunicationException(EmaException):
    """
    Exception to be thrown when a communication problems occur.
    """
    def __init__(self, msg=None, *args):
        super().__init__(self, msg, *args)