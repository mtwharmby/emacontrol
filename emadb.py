from datetime import datetime, timedelta
import sqlite3


def __sql_query__(conn, sql):
    pass
    """ TODO
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        cur.execute(SQL)
        return cur.fetchall()
        See:
        http://www.sqlitetutorial.net/sqlite-python/sqlite-python-select/
    """


def get_session_id_for_today(conn, delta=1):
    """
    Determine the ID of session within delta days of today

    Parameters
    ----------
    conn : a connection to an SQLite database
    delta : (optional) integer number of days difference between today and a 
            session date

    Returns
    -------
    integer : id of session

    Raises
    ------
    Exception : if no session in the database within delta days
    """
    today = datetime.now().date()
    result = __sql_query__(conn, ("""SELECT * FROM Sessions"""))
    for row in result:
        session_date = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S.%f").date()
        print(session_date)
        date_diff = abs(session_date - today)
        if date_diff <= timedelta(days=delta):
            return row[0]
    raise Exception(
        'No session with a date less than {} day before/aftertoday'
        .format(delta))


def get_appids_for_session(conn, session_id=None):
    """
    Get all application IDs associated with a specific session in the database

    Parameters
    ----------
    conn : a connection to an SQLite database
    session_id : (optional) integer representing a given session. If not given,
                 session_id is determined using get_session_id_for_today()

    Returns
    -------
    list : integers representing the application IDs
    """
    if session_id is None:
        session_id = get_session_id_for_today(conn)

    app_ids = []
    result = __sql_query__(conn, ("""SELECT application_id FROM Applications
                                     WHERE session_id=?""", (session_id,)))
    for row in result:
        app_ids.append(row[0])
    return app_ids


def get_samples_for_appid(conn, measurement, app_id):
    """
    For a given application ID, get all of the samples which are to be measured
    with a given measurment type

    Parameters
    ----------
    conn : a connection to an SQLite database
    measurement : string, either PXRD or PDF
    app_id : integer representing application ID

    Returns
    -------
    dict : keys are integer positions of samples in magazine,
           values are names of samples

    Raises
    ------
    KeyError : if measurement type other than 'PXRD' or 'PDF' is requested
    """
    measurement_sql = {'PXRD': """SELECT holder_position,user_sample_name FROM
                                  PXRD_Samples WHERE application_id=?""",
                       'PDF': """SELECT holder_position,user_sample_name FROM
                                  PDF_Samples WHERE application_id=?""",
                       }

    samples = {}
    result = __sql_query__(conn, (measurement_sql[measurement], (app_id,)))
    for row in result:
        samples[row[0]] = row[1]
    return samples
