from datetime import datetime,date
import json
from enum import Enum

from edu_app.db.cassandra import get_cassandra_session

def log_query(user_id: str, query_text: str, params: dict | None = None):
    """
    This function allows us to store the queries we do on mongo.
    we store:
        The date: date of today
        Time Stamp: Date and Time
        User ID
        Query text: A description of the query we did
        Query Params: params: extra information on a dict format
    """
    session = get_cassandra_session()

    cql='''
        INSERT INTO query_audit(log_date, ts, user_id, query_text, params) 
        VALUES(%s, %s, %s, %s, %s)
        '''


    now_ts = datetime.utcnow()
    today = date.today()

    params_json = json.dumps(params) if params is not None else None

    session.execute(cql, (today,now_ts, user_id, query_text, params_json))

    return {
        "status": "ok",
        "log_date": str(today),
        "ts": now_ts.isoformat()
    }

def log_security_event(user_id: str,  action: str, details:str | None = None):
    """
    This function allows us to store some security related issues
    (like failed or successful login attempts):
        User ID: logged user
        Time Stamp: Date and Time
        Action: What was done
        Details: Extra information about what was done
    """
    session = get_cassandra_session()
    cql = '''
        INSERT INTO security_logs(user_id, ts, action, details)
        VALUES (%s, %s, %s, %s)
    '''
    now_ts = datetime.utcnow()

    details_json = json.dumps(details) if details is not None else None

    session.execute(cql,(user_id, now_ts, action, details_json))

    return {
        'status': 'ok',
        'ts': now_ts.isoformat()
    }
def log_lesson_progress(user_id: str, course_id: str, lesson_id: str, status: str = "no_entregada"):
    """
    This function allows us to store the progress on lessons of the users on
    dedicated courses :
        User ID
        Course ID
        Lesson ID
        Time Stamp: Date and Time
        Status: Entregada o no Entregada
    """
    session = get_cassandra_session()
    if isinstance(status, Enum):
        final_status = status.value
    else:
        final_status = status or "no_entregada"
    cql = """
        INSERT INTO lesson_progress (user_id, course_id, lesson_id, ts, status)
        VALUES (%s, %s, %s, %s, %s)
    """

    now_ts = datetime.utcnow()

    session.execute(
        cql,
        (user_id, course_id, lesson_id, now_ts, final_status)
    )

    return {
        "status": "ok",
        "ts": now_ts.isoformat()
    }





