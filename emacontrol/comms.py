import socket
import time

from emacontrol.exceptions import EmaCommunicationException


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
        """
        self.socket.send(cmd)
        if await:
            self.__await_recv(await, timeout)

    def send_config(self, cmd, ready_signal, config, complete_signal, timeout=10):
        self.socket.send(cmd)
        self.__await_recv(ready_signal, timeout)
        self.socket.send(config)
        self.__await_recv(complete_signal, timeout)

    def __await_recv(self, await, timeout):
        """
        Waits for data of value await to arrive in the socket recv buffer. If none
        :param await: String, the arrival of which is being waited for
        :param timeout: Dime in seconds to wait for data
        :raises EmaCommunicationException if timeout reached
        """
        while self.socket.recv(16) != await:
            time.sleep(1)
            timeout -= 1
            if timeout <= 0:
                raise EmaCommunicationException("Timed out waiting for response '{}' from '{}:{}'".format(await, self.address, self.port))
