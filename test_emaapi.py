'''
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
'''
from mock import patch

from emaapi import (power_on)


@patch('emaapi.ema.send')
def test_power_on(ema_send_mock):
    power_on()

    ema_send_mock.assert_called_with('powerOn')
