import socket
import pytest

from emacontrol.network import SocketConnector


@pytest.fixture
def mock_sock(mocker):
    sock = mocker.MagicMock()
    sock().fileno.return_value = 2048
    sock().send.side_effect = lambda arg: len(arg)
    return sock


@pytest.fixture
def mock_sock_ctxman(mocker, mock_sock):
    ctxman = mocker.MagicMock()
    ctxman().__enter__.return_value = mock_sock()
    return ctxman


@pytest.fixture
def socket_patcher(monkeypatch, mock_sock_ctxman):
    monkeypatch.setattr(socket, 'socket', mock_sock_ctxman)


def test_SocketConnector_init():
    sock_conn = SocketConnector('emahost.desy.de', 5432)

    assert sock_conn.peer == ('emahost.desy.de', 5432)
    assert sock_conn.socket_timeout == 120


@pytest.mark.parametrize('msg, expected_msg',
                         [['ACommandWithParameters:#P1#P2;',
                          'ACommandWithParameters:#P1#P2;'.encode()]])
def test_sendonly(mock_sock, msg, expected_msg):
    # TODO Test chunking
    sock_conn = SocketConnector(host='127.0.0.3', port=10006)

    sock_conn.__sendonly__(mock_sock(), msg)
    mock_sock().send.assert_called_with(expected_msg)


@pytest.mark.parametrize('reply', [
    'ACommandWithParameters:#P1#P2;'
])
def test_recvonly(mock_sock, reply):
    # TODO Test chunking
    # TODO Test null stripping
    mock_sock().recv.return_value = reply.encode()

    sock_conn = SocketConnector(host='127.0.0.3', port=10006)
    msg = sock_conn.__recvonly__(mock_sock())

    assert msg == reply
    mock_sock().recv.assert_called_with(1024)


@pytest.mark.parametrize(
    'message, reply',
    [('ACommandWithParameters:#P1#P2;', 'ACommandWithParameters:done;'),
     ]
)
def test__send__(socket_patcher, mock_sock, mock_sock_ctxman, message, reply):
    mock_sock().recv.return_value = reply.encode()

    sock_conn = SocketConnector(host='127.0.0.3', port=10006)
    answer = sock_conn.__send__(message)

    mock_sock_ctxman.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
    mock_sock().connect.assert_called_with(
        ('127.0.0.3', 10006)
    )
    mock_sock().send.assert_called_with(message.encode())
    assert answer == reply


@pytest.mark.parametrize(
    'message, reply',
    [('UndelimitedOutboundMessage', 'WillNotBeReceived;'),
     ('DelimitedOutboundMessage;', 'UndelimitedReply')]
)
def test__send__delimiter_error(socket_patcher, mock_sock, mock_sock_ctxman,
                                message, reply):
    sock_conn = SocketConnector(host='127.0.0.3', port=10006,
                                socket_timeout=0.5)
    assert sock_conn.socket_timeout == 0.5

    with pytest.raises(RuntimeError) as exc:
        sock_conn.__send__(message)

        assert 'No message delimiter' in str(exc)
