"""
Output needs to be a dictionary of application_IDs, each with a dictionary of sample position : sample name

To do this, get list of applications from DB - based on session (this determined from date?)
Then get list of all samples in table with that app_ID - which table?
"""
from datetime import date

import pytest
from mock import Mock, patch

from emadb import (get_appids_for_session, get_samples_for_appid,
                   get_session_id, get_samples_for_measurement_for_session)


@patch('emadb.date')
def test_get_session_id(dt_mock):
    # Mocking datetime.today() is special as it's a built-in C function
    # Explanation of how to do this in Mock docs:
    # https://docs.python.org/3/library/unittest.mock-examples.html#partial-mocking
    # N.B. We are not mocking datetime.date, but emadb.date. 
    dt_mock.today.return_value = date(2019, 6, 19)
    dt_mock.side_effect = lambda *args, **kw: date(*args, **kw)

    with patch('emadb.SQLiteConnector') as sql_mock:
        sql_mock.query_rows.return_value = [(1, '2019-06-19 09:00:00.000'),
                                            (2, '2019-07-14 09:00:00.000')]

        session_id = get_session_id(sql_mock)
        assert session_id == 1

        with pytest.raises(Exception,
                           match=r".*session with a date less than .*"):
            sql_mock.query_rows.return_value = [(1, '1019-06-19 09:00:00.000'),
                                                (2, '1019-07-14 09:00:00.000')]

            session_id = get_session_id(sql_mock)


def test_get_appids_for_session():

    with patch('emadb.SQLiteConnector') as sql_mock:
        sql_mock.query_rows.return_value = [(120,), (522,), (742,)]

        app_ids = get_appids_for_session(sql_mock, session_id=1)
        sql_mock.query_rows.assert_called_with(
            """SELECT application_id FROM Applications WHERE session_id=?""",
            (1,))
        assert app_ids == [120, 522, 742]


def test_get_samples_for_appid():

    with patch('emadb.SQLiteConnector') as sql_mock:
        sql_mock.query_rows.return_value = [(1, 'sample A',), (2, 'sample Q')]

        # Check getting PXRD samples...
        samples = get_samples_for_appid(sql_mock, 'PXRD', 120)

        sql_mock.query_rows.assert_called_with(
            """SELECT holder_position,user_sample_name FROM PXRD_Samples WHERE
           application_id=?""",
            (120,))
        assert samples == {1: 'sample A', 2: 'sample Q'}

        # Check getting PDF samples...
        samples = get_samples_for_appid(sql_mock, 'PDF', 120)
        sql_mock.query_rows.assert_called_with(
            """SELECT holder_position,user_sample_name FROM PDF_Samples WHERE
           application_id=?""",
            (120,))

        # Check getting some non-existant measurement type...
        # ... this should throw an error
        with pytest.raises(KeyError, match=r"LightScattering"):
            samples = get_samples_for_appid(sql_mock, 'LightScattering', 120)


@patch('emadb.get_session_id')
def test_get_samples_for_measurement_for_session(sessid_mock):
    sql_mock = Mock('DB Connector')
    sessid_mock.return_value = 1

    with patch('emadb.get_appids_for_session') as appids_mock:
        with patch('exmadb.get_samples_for_appid') as samples_mock:
            appids_mock.return_value = [120, 522, 742]
            samples_mock.side_effect = [
                {1: 'sample A', 2: 'sample Q'},
                {4: 'badger', 8: 'cupcake'},
                {10: 'MTW656', 53: 'MTW754'}
            ]

            all_samples = get_samples_for_measurement_for_session(sql_mock, 
                                                                  'PXRD')
            assert all_samples == {
                120: {1: 'sample A', 2: 'sample Q'},
                522: {4: 'badger', 8: 'cupcake'},
                742: {10: 'MTW656', 53: 'MTW754'}
            }
