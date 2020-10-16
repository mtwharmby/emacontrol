
# def test_set_sample_mounted():
#     with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
#         ema = Robot()

#         send_mock.return_value = 'sampleMounted:done;'
#         ema.set_sample_mounted(True)
#         send_mock.assert_called_with('sampleMounted;')

#         send_mock.return_value = 'sampleUnmounted:done;'
#         ema.set_sample_mounted(False)
#         send_mock.assert_called_with('sampleUnmounted;')


# def test_get_spin_position_offset():
#     with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
#         ema = Robot()
#         send_mock.return_value = (
#             'getSpinPosOffset:#X2.685#Y5.211#Z-8.646;'
#         )  # This is raw output from the robot, hence __send__
#         res = ema.get_spin_position_offset()
#         assert res == {'x': 2.685, 'y': 5.211, 'z': -8.646}


# def test_set_spin_position_offset():
#     with patch('emacontrol.emaapi.Robot.send') as send_mock:
#         ema = Robot()
#         ema.set_spin_position_offset(7, 6, 2)
#         send_mock.assert_called_with(('setSpinPosOffset:#X7.000#Y6.000'
#                                       + '#Z2.000;'),
#                                      wait_for='setSpinPosOffset:done;')


# def test_get_spin_home_position():
#     with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
#         ema = Robot()
#         send_mock.return_value = (
#             'getSpinHomePosition:#X26.785#Y52.111#Z86.146#RX0.841#RY89.653'
#             + '#RZ-0.064;'
#         )  # This is raw output from the robot, hence __send__
#         res = ema.get_spin_home_position()
#         assert res == {'x': 26.785, 'y': 52.111, 'z': 86.146,
#                        'rx': 0.841, 'ry': 89.653, 'rz': -0.064}


# def test_get_spin_position():
#     with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
#         ema = Robot()
#         send_mock.return_value = (
#             'getSpinPosition:#X29.47#Y57.322#Z77.5#RX0.841#RY89.653#RZ-0.064;'
#         )  # This is raw output from the robot, hence __send__
#         res = ema.get_spin_position()
#         assert res == {'x': 29.47, 'y': 57.322, 'z': 77.5,
#                        'rx': 0.841, 'ry': 89.653, 'rz': -0.064}


# def test_get_diffr_origin():
#     with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
#         send_mock.return_value = ('getDiffOrigin:#X22.47#Y50.322#Z70.5;')

#         ema = Robot()
#         res = ema.get_diffr_origin_calib()
#         assert res == CoordsXYZ(22.47, 50.322, 70.5)


# def test_set_diffr_origin():
#     pass


# def test_get_diffr_pos_calib():
#     with patch('emacontrol.emaapi.Robot.__send__') as send_mock:
#         send_mock.return_value = ('getDiffRel:#X7.0#Y6.232#Z-1.866;')

#         ema = Robot()
#         res = ema.get_diffr_pos_calib()
#         assert res == CoordsXYZ(7.0, 6.232, -1.866)


# def test_set_diffr_pos_calib():
#     pass