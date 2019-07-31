import socket

import pytest
from mock import call, patch

from emacontrol.network import SocketConnector


def test_read_config():
    sock_conn = SocketConnector(None, None, config_file='./example_config.ini')
    sock_conn._read_config()
    assert sock_conn.peer == ('127.0.0.2', 10005)


@patch('socket.socket')
def test_is_connected(sock_mock):
    sock_conn = SocketConnector(host='127.0.0.3', port=10006)

    assert sock_conn.is_connected() is False

    # A normal connection
    sock_conn._connect()
    # fileno = 11 happens when a socket connects (fileno != -1)
    sock_mock().fileno.return_value = 11
    assert sock_conn.is_connected() is True

    # Fake a broken connection (fileno goes to -1)
    sock_mock().fileno.return_value = -1
    assert sock_conn.is_connected() is False


@patch('socket.socket')
def test__connect__disconnect(sock_mock):
    sock_conn = SocketConnector(host='127.0.0.3', port=10006)

    # A normal connection
    sock_conn._connect()
    # fileno = 11 happens when a socket connects (fileno != -1)
    sock_mock().fileno.return_value = 11
    assert sock_conn.is_connected() is True

    sock_conn._disconnect()
    assert sock_conn.is_connected() is False
    # we don't set the fileno here as disconnect should set sock = None


@patch('socket.socket')
def test__send__(sock_mock):
    # The test assume that the socket is always correctly connected when
    # fileno is queried
    sock_mock().fileno.return_value = 11

    message = 'ACommandWithParameters:#P1#P2;'
    msg_reply = 'ACommandWithParameters:done;'
    sock_mock().send.return_value = len(message)
    sock_mock().recv.return_value = msg_reply.encode()

    sock_conn = SocketConnector(host='127.0.0.3', port=10006)
    reply = sock_conn.__send__(message)

    assert reply == msg_reply
    sock_calls = [call.connect(('127.0.0.3', 10006)),
                  call.send(message.encode()),
                  call.shutdown(socket.SHUT_WR),
                  call.recv(1024),
                  call.fileno(),  # This from is_connected()
                  call.close()]
    sock_mock().assert_has_calls(sock_calls)

    # Same again, but now the messages are sent and received in pieces
    sock_mock().reset_mock(return_value=True, side_effect=True)
    sock_mock().send.side_effect = [5, 10, 7, 8]
    sock_mock().recv.side_effect = [b'ACommandWithP',
                                    b'arameters:',
                                    b'done;']

    sock_conn = SocketConnector(host='127.0.0.3', port=10006)
    reply = sock_conn.__send__(message)

    assert reply == msg_reply

    # Now test what happens when no message delimiter is received
    sock_mock().reset_mock(return_value=True, side_effect=True)
    sock_mock().send.reset_mock(return_value=True, side_effect=True)
    sock_mock().recv.reset_mock(return_value=True, side_effect=True)

    msg_reply = 'ACommandWithParameters:done'  # N.B. Removed delimiter
    sock_mock().send.return_value = len(message)
    sock_mock().recv.return_value = msg_reply.encode()

    sock_conn = SocketConnector(host='127.0.0.3', port=10006, socket_timeout=0.5)
    with pytest.raises(RuntimeError, match=r".*delimiter.*"):
        reply = sock_conn.__send__(message)