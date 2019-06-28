"""
Output needs to be a dictionary of application_IDs, each with a dictionary of sample position : sample name

To do this, get list of applications from DB - based on session (this determined from date?)
Then get list of all samples in table with that app_ID - which table?
"""
from datetime import datetime

import pytest
from mock import patch, Mock

from emadb import (get_appids_for_session, get_samples_for_appid,
                   get_session_id_for_today)


@patch('datetime.datetime')
def test_get_session_id_for_today(dt_mock):
    dbconn_mock = Mock()
    dt_mock.now().return_value = datetime(2019, 6, 19)

    with patch('emadb.SQLiteConnector.query_rows') as sql_mock:
        sql_mock.return_value = [(1, '2019-06-19 09:00:00.000'),
                                 (2, '2019-07-14 09:00:00.000')]

        session_id = get_session_id_for_today(dbconn_mock)
        assert session_id == 1

        with pytest.raises(Exception,
                           match=r".*session with a date less than .*"):
            sql_mock.return_value = [(1, '1019-06-19 09:00:00.000'),
                                     (2, '1019-07-14 09:00:00.000')]

            session_id = get_session_id_for_today(dbconn_mock)


def test_get_appids_for_session():
    dbconn_mock = Mock()

    with patch('emadb.SQLiteConnector.query_rows') as sql_mock:
        sql_mock.return_value = [(120,), (522,), (742,)]

        app_ids = get_appids_for_session(dbconn_mock, session_id=1)
        sql_mock.assert_called_with(dbconn_mock, ("""SELECT application_id FROM Applications
                                     WHERE session_id=?""", (1,)))
        assert app_ids == [120, 522, 742]


def test_get_samples_for_appid():
    dbconn_mock = Mock()

    with patch('emadb.SQLiteConnector.query_rows') as sql_mock:
        sql_mock.return_value = [(1, 'sample A',), (2, 'sample Q')]

        # Check getting PXRD samples...
        samples = get_samples_for_appid(dbconn_mock, 'PXRD', 120)
        sql_mock.assert_called_with(dbconn_mock, (
            """SELECT holder_position,user_sample_name FROM
                                  PXRD_Samples WHERE application_id=?""",
                                   (120,)))
        assert samples == {1: 'sample A', 2: 'sample Q'}

        # Check getting PDF samples...
        samples = get_samples_for_appid(dbconn_mock, 'PDF', 120)
        sql_mock.assert_called_with(dbconn_mock, (
            """SELECT holder_position,user_sample_name FROM
                                  PDF_Samples WHERE application_id=?""",
                                   (120,)))

        # Check getting some non-existant measurement type...
        # ... this should throw an error
        with pytest.raises(KeyError, match=r"LightScattering"):
            samples = get_samples_for_appid(dbconn_mock, 'LightScattering',
                                            120)
