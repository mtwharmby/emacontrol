from datetime import datetime, timedelta


class SQLiteConnector():
    import sqlite3
    """
    This connector provides all the database connectivity to an SQLite
    database. The pattern is based on the idea suggested in
    https://softwareengineering.stackexchange.com/questions/200522/how-to-deal-with-database-connections-in-a-python-library-module 
    by "Travis"
    """

    def __init__(self, db_file):
        self.connection = self.sqlite3.connect(db_file)

    def query(self, query, params=()):
        """
        Submit an SQL query to the database and get the resulting cursor

        Parameters
        ----------
        query : String SQL query with
        params : (optional) tuple or dictionary of parameters/named parameters

        Returns
        -------
        Cursor : cursor containing result of query
        """
        with self.connection:
            cursor = self.connection.cursor()
            return cursor.execute(query, params)

    def query_rows(self, query, params=()):
        """
        Submit an SQL query to the database and get the resulting rows

        Parameters
        ----------
        query : String SQL query with
        params : (optional) tuple or dictionary of parameters/named parameters

        Returns
        -------
        list : rows of results from the query
        """
        # TODO Add rowfactory optional arg
        return self.query(query, params).fetchall()

    def __del__(self):
        """
        Delete function called by garbage collector when object falls out of
        scope.
        """
        self.connection.close()


def get_session_id_for_today(db_connector, delta=1):
    """
    Determine the ID of session within delta days of today

    Parameters
    ----------
    db_connector : object to manage database connections
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
    result = db_connector.query_rows("""SELECT * FROM Sessions""")
    for row in result:
        session_date = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S.%f").date()
        date_diff = abs(session_date - today)
        if date_diff <= timedelta(days=delta):
            return row[0]
    raise Exception(
        'No session with a date less than {} day before/aftertoday'
        .format(delta))


def get_appids_for_session(db_connector, session_id=None):
    """
    Get all application IDs associated with a specific session in the database

    Parameters
    ----------
    db_connector : object to manage database connections
    session_id : (optional) integer representing a given session. If not given,
                 session_id is determined using get_session_id_for_today()

    Returns
    -------
    list : integers representing the application IDs
    """
    if session_id is None:
        session_id = get_session_id_for_today(db_connector)

    app_ids = []
    result = db_connector.query_rows(
        """SELECT application_id FROM Applications WHERE session_id=?""",
        (session_id,))
    for row in result:
        app_ids.append(row[0])
    return app_ids


def get_samples_for_appid(db_connector, measurement, app_id):
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
    # This could be done without using the PXRD_Samples/PDF_Samples views.
    # That might make the measurement selection a little cleaner
    measurement_sql = {'PXRD':
                       """SELECT holder_position,user_sample_name FROM
                       PXRD_Samples WHERE application_id=?""",
                       'PDF':
                       """SELECT holder_position,user_sample_name FROM
                       PDF_Samples WHERE application_id=?""",
                       }

    samples = {}
    result = db_connector.query_rows(measurement_sql[measurement], (app_id,))
    for row in result:
        samples[row[0]] = row[1]
    return samples


""" TODO
    function: get samples for session - measurement, session_id(opt)
    get appids
    for appids get samples (for measurement)
    restructure & return
"""
