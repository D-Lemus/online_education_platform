from datetime import datetime,date
import json

from edu_app.db.cassandra import get_cassandra_session

def log_query(user_id: str, query_text: str, params: dict | None = None):

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

def log_security_event(user_id: str,    action: str,    ip: str | None = None,    details: dict | None = None):
    session = get_cassandra_session()
    cql = '''
        INSERT INTO security_logs (user_id, ts, action, ip, details)
        VALUES (%s, %s, %s, %s, %s)
    '''
    now_ts = datetime.utcnow()
    details_json = json.dumps(details) if details is not None else None

    session.execute(cql,(user_id, now_ts, action, ip, details_json))

    return {
        'status': 'ok',
        'ts': now_ts.isoformat()
    }