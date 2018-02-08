import mock
from emacontrol.comms import RobotSocket, EmaCommunicationException

class TestRobotSocket:
    def setUp(self):
        pass

    def test_connect(self):
        """
        Tests socket is correctly configured by arguments
        """
        with mock.patch('socket.socket') as mock_socket:
            r_sock = RobotSocket("192.168.58.38", 10004) #Is there a DNS name rather than an IP addy?
        r_sock.socket.connect.assert_called_with(("192.168.58.38", 10004))

    def test_send(self):
        """
        Tests sending a message to a (mock) socket
        """
        with mock.patch('socket.socket') as mock_socket:
            r_sock = RobotSocket("192.168.58.38", 10004)
            r_sock.send_cmd("shrtmsg")

        r_sock.socket.send.assert_called_with("shrtmsg")

    def test_send_recv(self):
        """
        Tests sending a message and receiving a (correct) reply
        """
        with mock.patch('socket.socket') as mock_socket:
            mock_socket.return_value.recv.return_value = "right"

            r_sock = RobotSocket("192.168.58.38", 10004)
            r_sock.send_cmd("reply", await="right")

        r_sock.socket.send.assert_called_with("reply")
        r_sock.socket.recv.assert_called()

    def test_wrong_reply(self):
        """
        Tests sending a message and receiving an unexpected reply
        """
        with mock.patch('socket.socket') as mock_socket:
            mock_socket.return_value.recv.return_value = "wrong"

            r_sock = RobotSocket("192.168.58.38", 10004)
            try:
                r_sock.send_cmd("reply", await="correct", timeout=3)
            except EmaCommunicationException:
                pass #Expected

        r_sock.socket.send.assert_called_with("reply")
        r_sock.socket.recv.assert_called()

    def test_send_config(self):
        """
        Tests sending a command which should be followed by additional
        configuration data for the VAL3 layer
        """
        with mock.patch('socket.socket') as mock_socket:
            mock_socket.return_value.recv.side_effect = ["setXaxis:waiting","setXaxis:done"]

            r_sock = RobotSocket("192.168.58.38", 10004)
            r_sock.send_config("defx", "setXaxis:waiting", 42, "setXaxis:done", timeout=3)

        r_sock.socket.send.call_args_list = ["defx", "42"]
        r_sock.socket.recv.assert_called()