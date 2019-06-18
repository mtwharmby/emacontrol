import sqlite3


def __sql_query__(conn, sql):
    pass


def get_session_id_for_today(conn):
    pass


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
