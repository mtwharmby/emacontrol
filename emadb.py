import sqlite3


def __sql_query__(conn, sql):
    pass


def get_appids_for_session(conn, session_id=None):
    app_ids = []
    result = __sql_query__(conn, ("""SELECT application_id FROM Applications
                                     WHERE session_id=?""", (session_id,)))
    for row in result:
        app_ids.append(row[0])
    return app_ids


def get_samples_for_appid(conn, measurement, app_id):
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
