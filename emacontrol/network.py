import socket
import time

try:
    from gevent.coros import BoundedSemaphore
except ImportError:
    from gevent.lock import BoundedSemaphore

_send_recv_semaphore = BoundedSemaphore()


class SocketConnector(object):

    def __init__(self, host, port, socket_timeout=120):
        self.peer = (host, port)
        self.socket_timeout = socket_timeout

    def __sendonly__(self, sock, message):
        """
        Sends message using the given sock

        Uses send function of socket. If entire message cannot be sent in one
        send call, the function breaks up the message and sends it in parts to
        the peer.

        Parameters
        ----------
        sock : socket.socket
        A connected socket object.

        message : str
        A string message to send. Must have a ";" at the end to delimit it.
        """
        if ';' not in message:
            raise RuntimeError('No message delimiter. Cannot send.')
        msg_bytes = str(message).encode()
        bytes_sent = 0
        send_start = time.time()
        while bytes_sent < len(msg_bytes):
            bytes_sent = bytes_sent + sock.send(msg_bytes)
            if (time.time() - send_start) > self.socket_timeout:
                # TODO Log: 'Failed to send message within timeout
                # ({})'.format(self.socket_timeout)
                msg = 'Message not sent before timeout'
                raise RuntimeError(msg)
            # TODO Log: 'Sent message "{}" on socket

    def __recvonly__(self, sock):
        """
        Receives messages from peer using the given socket

        Uses recv function of socket. Continuously receives bytes from the
        peer until a ";" is received. Any null bytes are stripped from the
        messages.

        Parameters
        ----------
        sock : socket.socket
        A connected socket object.

        Returns
        -------
        msg : str
        Reassembled delimited message. Decoded to UTF-8 from bytes.
        """
        msg_chunks = []
        recv_start = time.time()
        while True:
            chunk = sock.recv(1024)
            chunk = chunk.strip(b'\x00').decode('utf-8')
            msg_chunks.append(chunk)
            if chunk.count(';') == 1:
                break
            if (time.time() - recv_start) > self.socket_timeout:
                msg = 'No message delimiter received before timeout'
                raise RuntimeError(msg)

        return "".join(msg_chunks)

    def __send__(self, message):
        """
        Send a string message and get a reply

        Creates a socket and makes a connection to the peer specified on
        instantiation of this SocketConnector object. Message is sent to the
        peer and the received reply is then returned. Socket is closed by the
        context manager.

        Parameters
        ----------
        message : str
        String message to send to peer. Must be delimited with a ";".

        Returns
        -------
        reply : str
        String message received from peer, delimited with a ";".
        """
        # Context manager handles socket creation and closing
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.peer)
            # with-block ensures no other send attempts happen simultaneously
            with _send_recv_semaphore:
                self.__sendonly__(sock, message)

                # This is commented out as, although it is the 'correct' thing
                # to do, it seems to have a detrimental effect on the stability
                # of the code. Messages never get answered.
                #
                # Message fully sent, so we indicate no further sends
                # self.sock.shutdown(socket.SHUT_WR)

                # Now we wait for a reply
                full_msg = self.__recvonly__(sock)

        # Put the message back together and check it's what we expected
        return full_msg
