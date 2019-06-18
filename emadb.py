import sqlite3


def __sql_query__(conn, sql):
    pass


def get_appids_for_session(conn, session_id=None):
    app_ids = []
    result = __sql_query__(conn, 
                           ('SELECT application_id FROM Applications WHERE\
                               session_id=?', (session_id,)))
    for row in result:
        app_ids.append(row[0])
    return app_ids
