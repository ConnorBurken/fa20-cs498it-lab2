import os
import time
import sqlite3

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

sql_create_table = '''
CREATE TABLE sensor_log (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	room_id TEXT(2000000000) NOT NULL,
	sensor_id TEXT(2000000000) NOT NULL,
	"value" INTEGER NOT NULL,
	ts INTEGER NOT NULL
);
'''

sql_insert = '''
INSERT INTO sensor_log
(room_id, sensor_id, "value", ts)
VALUES('{0}', '{1}', {2}, {3});
'''

sql_query_by_room_id_and_ts_range = '''
SELECT * FROM sensor_log
WHERE room_id='{0}' and ts > {1} and ts < {2}
ORDER BY ts DESC
'''

db = {
    "file_name": "db/data.sqlite",
    "conn": None
}


def init_db():
    db_file = os.path.join(__location__, db['file_name'])
    print('db_file = {0}'.format(db_file))

    if not os.path.exists(db_file):
        print('Creating new db file...')

        with open(db_file, 'w') as fp:
            pass

        print('Connecting to db...')
        db['conn'] = sqlite3.connect(db_file, check_same_thread=False)

        print('Creating table...')
        db['conn'].execute(sql_create_table)

    else:
        print('Connecting to db...')
        db['conn'] = sqlite3.connect(db_file, check_same_thread=False)


def insert_record(room_id, sensor_id, value):
    if db['conn'] is None:
        init_db()

    print('inserting record: room_id = {0}; sensor_id = {1}; value = {2}'.format(room_id, sensor_id, value))
    db['conn'].cursor().execute(sql_insert.format(room_id, sensor_id, value, int(round(time.time() * 1000))))
    db['conn'].commit()


def query_record(room_id, ts_start, ts_end):
    if db['conn'] is None:
        init_db()

    print('querying records: room_id = {0}; ts_start = {1}; ts_end = {2}'.format(room_id, ts_start, ts_end))
    rows = db['conn'].cursor().execute(sql_query_by_room_id_and_ts_range.format(room_id, ts_start, ts_end))

    results = []
    for row in rows:
        results.append({
            'room_id': row[1],
            'sensor_id': row[2],
            'value': row[3],
            'ts': row[4]
        })

    return results
