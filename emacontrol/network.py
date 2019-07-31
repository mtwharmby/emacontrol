import configparser
import socket
import time
import os

from emacontrol.utils import input_to_int

try:
    from gevent.coros import BoundedSemaphore
except ImportError:
    from gevent.lock import BoundedSemaphore

_send_recv_semaphore = BoundedSemaphore()


class SocketConnector(object):

    def __init__(self, host, port, config_file=None, socket_timeout=60):
        self.peer = (host, port)
        self.sock = None
        self.socket_timeout = socket_timeout
        self.config_file = config_file

    def _read_config(self):
        '''
        Read the configuration for the socket from the configuration file given
        to the robot at initialisation. Currently only the hostname/IP address
        and the port are read from the config_file. See example_config.ini to
        see the structure of the config.
        '''
        # FIXME Make this non-robot specific
        # TODO Log: 'Reading config file {}'.format(self.config_file)
        if not os.path.exists(self.config_file):
            raise(FileNotFoundError('Cannot find E.M.A. API config file: {}'
                                    .format(self.config_file)))
        confparse = configparser.ConfigParser()
        confparse.read(self.config_file)

        # Read values from config ensuring port is integer > 0
        robot_host = confparse.get('robot', 'address')
        robot_port = input_to_int(confparse.get('robot', 'port'))
        if robot_port <= 0:
            raise ValueError('Expecting value greater than 0')
        self.peer = (robot_host, robot_port)
        # TODO Log: 'Socket peer for this connection set to "{}:{}"'.format(*self.peer)

    def _connect(self):
        '''
        Connect a socket to the robot controller
        '''
        # TODO Log: 'Connecting socket...'
        if self.is_connected():
            # TODO Log: 'Socket already connected to "{}:{}"'.format(*self.sock.getpeername()))
            return
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if (self.peer[0] is None) or (self.peer[1] is None):
            self._read_config()
        self.sock.connect(self.peer)
        # TODO Log: 'Socket connected to {}:{}'.format(self.address, self.port)

    def _disconnect(self):
        """
        Disconnect active socket (if one exists)
        """
        # TODO Log: 'Disconnecting socket...'
        if self.is_connected():
            # TODO socket_info = self.sock.getpeername()
            self.sock.close()
            self.sock = None
            # TODO Log: 'Closed socket to {}:{}'.format(*socket_info)
            return
        # TODO Log: 'Socket is already disconnected'

    def is_connected(self):
        """
        Reports whether a socket is connected
        (i.e. it exists and has a file ID != -1)
        """
        # print('sock: {} fileno: {}'.format(self.sock, self.sock.fileno()))
        if self.sock is None:
            return False
        return self.sock.fileno() is not -1

    def __send__(self, message):
        """
        Send is a protected method which separates the handling of the socket
        interactions from the interpretation of the message. To send messages
        to the robot, use the send method.
        """
        self._connect()

        # with-block ensures no other send attempts happen simultaneously
        with _send_recv_semaphore:
            msg_bytes = str(message).encode()
            bytes_sent = 0
            send_start = time.time()
            while bytes_sent < len(msg_bytes):
                bytes_sent = bytes_sent + self.sock.send(msg_bytes)
                if (time.time() - send_start) > self.socket_timeout:
                    # TODO Log: 'Failed to send message within timeout ({})'.format(self.socket_timeout)
                    msg = 'Message not sent before timeout'
                    raise RuntimeError(msg)
                # TODO Log: 'Sent message "{}" on socket

            # This is commented out as, although it is the 'correct' thing to
            # do, it seems to have a detrimental effect on the stability of
            # the code. Messages never get answered.
            #
            # Message fully sent, so we indicate no further sends
            # self.sock.shutdown(socket.SHUT_WR)

            # Now we wait for a reply
            msg_chunks = []
            recv_start = time.time()
            while True:
                chunk = self.sock.recv(1024)
                chunk = chunk.strip(b'\x00').decode('utf-8')
                msg_chunks.append(chunk)
                if chunk.count(';') == 1:
                    break
                if (time.time() - recv_start) > self.socket_timeout:
                    msg = 'No message delimiter received before timeout'
                    raise RuntimeError(msg)

        # We're done, close the socket
        self._disconnect()

        # Put the message back together and check it's what we expected
        return "".join(msg_chunks)
