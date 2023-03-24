from app import app
from flask import Response, json, jsonify
from datetime import datetime
import re

# @app.route('/logs', methods=["GET"])
# def get_log():
#     with open('api.log', 'r') as f:
#         log_contents = f.readlines()
#     logs = []
#     for line in log_contents:
#         parts = line.strip().split(' ')
#         if len(parts) > 6:
#             user = parts[1]
#             time_str = ' '.join(parts[5:7])
#             message = ' '.join(parts[2:5]) + ' ' + ' '.join(parts[7:])
#             time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
#             logs.append({'time': time.strftime('%Y-%m-%d %H:%M:%S.%f'), 'message': message})
#     return Response(json.dumps(logs), mimetype='application/json')


# @app.route('/logs', methods=["GET"])
# def get_log():
#     with open('api.log', 'r') as f:
#         log_contents = f.readlines()
#     logs = []
#     for line in log_contents:
#         parts = line.strip().split(' ')
#         user = parts[1]
#         time = ' '.join(parts[5:7])
#         logs.append({'user': user, 'time': time})
#     return Response(json.dumps(logs), mimetype='application/json')


# Return text/file

@app.route('/logs', methods=["GET"])
def get_log():
    with open('api.log', 'r') as f:
        log_contents = f.read()
    return Response(log_contents, mimetype='text/plain')