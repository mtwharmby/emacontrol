"""
- power_on
- power_off
- start
- stop
- set_axis
- homing
- power_status
- mount_sample
- unmount_sample
- (status)
- (calibrate_sam)
- (compare_sam)
"""
from mock import patch

from emaapi import (power_off, power_on, reset, restart, start, stop)


@patch('emaapi.ema.send')
def test_power_off(ema_send_mock):
    power_off()
    ema_send_mock.assert_called_with('powerOff')


@patch('emaapi.ema.send')
def test_power_on(ema_send_mock):
    power_on()
    ema_send_mock.assert_called_with('powerOn')


@patch('emaapi.ema.send')
def test_reset(ema_send_mock):
    reset()
    ema_send_mock.assert_called_with('reset')


@patch('emaapi.ema.send')
def test_restart(ema_send_mock):
    restart()
    ema_send_mock.assert_called_with('restartMotor')


@patch('emaapi.ema.send')
def test_start(ema_send_mock):
    start()
    ema_send_mock.assert_called_with('start')


@patch('emaapi.ema.send')
def test_stop(ema_send_mock):
    stop()
    ema_send_mock.assert_called_with('stopMotor')
