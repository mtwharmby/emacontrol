import pytest

from emacontrol.ema import Response, Robot
from emacontrol.utils import TrsfMx, TrVect


def test_get_trsfmx(mocker):
    mocker.patch('emacontrol.emaapi.Robot.send', return_value=Response('getSpinHomePosition', 'ok', {'x': 0, 'y': 0, 'z': 0}))
    ema = Robot()
    
    print(ema.send('blah'))
    assert False


def test_get_trvect():
    pass
