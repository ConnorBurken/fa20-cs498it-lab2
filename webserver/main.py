import json
from flask import Flask, url_for, redirect, request, jsonify
from serial_util import get_serial_ports, select_serial_ports
# from serial_util_test import get_serial_ports, select_serial_ports
from db_util import insert_record, query_record

app = Flask(__name__)
status = {
    'serial_working': False,
    'ser': None,
    'data': {}
}


@app.route('/')
def favicon():
    return redirect(url_for('static', filename='index.html'))


@app.route('/hi')
def hello():
    return 'Hello, World!'


@app.route('/serial_list', methods=['GET', 'POST'])
def serial_get():
    if request.method == 'POST':
        req = request.get_json()
        print('selected port: {0}'.format(req['port']))
        select_serial_ports(req['port'], status)
        return jsonify({'result': 'ok'})
    else:
        return jsonify({'ports': get_serial_ports()})


@app.route('/status')
def get_status():
    return jsonify({
        'serial_working': status['serial_working'],
        'data': status['data']
    })


@app.route('/insert', methods=['POST'])
def insert():
    req = request.get_json()
    insert_record(req['room_id'], req['sensor_id'], req['value'])

    return jsonify({'result': 'ok'})


@app.route('/query', methods=['POST'])
def query():
    req = request.get_json()
    result = query_record(req['room_id'], req['ts_start'], req['ts_end'])

    return jsonify({'result': result})
