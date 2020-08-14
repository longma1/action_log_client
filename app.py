import json
from datetime import datetime

from dateutil import parser
from dateutil.parser import ParserError

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

# this disable an annoying warning when starting the app
# developers said this will be removed in the next 'major release', but that was back in 2015 and here we are now
# reference: https://github.com/pallets/flask-sqlalchemy/issues/365
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Models
class Log(db.Model):
    __tablename__ = 'log'
    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(32), unique=False, nullable=False)
    session_id = db.Column(db.String(32), unique=False, nullable=False)


class Actions(db.Model):
    __tablename__ = 'actions'
    action_id = db.Column(db.Integer, primary_key=True)
    # assuming we have finite number of action type I would have liked to change this to an ENUM field, but since I
    # do not have the complete list of all possible action type, this will be left as a string field.
    action_type = db.Column(db.String(16), unique=False, nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)

    # the best way I could think of storing the properties of each action would be to store each action as an object
    # in a NoSQL database with an unique id which would be stored here instead of the entire json object as a string,
    # but for now I will leave it as a string since I do not have much experience with setting that up,
    # nor is it required in the context of this assignment.
    properties = db.Column(db.String(256), unique=False, nullable=False)

    log_id = db.Column(db.Integer, db.ForeignKey('log.log_id'), nullable=False)
    log = db.relationship('Log', backref=db.backref('log', lazy=True))



@app.route("/log", methods=['POST'])
def log():
    """Extracts the log object in the json body of the request and store it in the database

     The function takes the json representation of a log event passed in the http post request stores it into the
     database based on the schema. The object is split into a Log component and an action component according to the
     schema above


     Returns: A json object that says success = true or false in an http response. The response code will be 200 for
     a successful POST operation and 400 for a failed operation
    """
    package = request.get_json()
    try:
        current_log = Log(user_id=package['userId'], session_id=package['sessionId'])
        db.session.add(current_log)
        for action in package['actions']:
            action = Actions(
                properties=json.dumps(action['properties']),
                action_type=action['type'],
                time=parser.parse(action['time']),
                log=current_log)
            db.session.add(action)

        db.session.commit()

        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except (KeyError, TypeError, ParserError) as e:
        db.session.flush()
        return json.dumps({'success': False, 'errorCode': 'Bad request'}), 400, {'ContentType': 'application/json'}


@app.route("/log", methods=['GET'])
def generate_report():
    """Generates array of logged events based on the criteria in the url query

     Takes url query parameters from the get request and generates the list of logged events that fits the criteria
     listed. This function expects up 4 query strings: userId, type, startTime, endTime, filtering based on the
     userId, eventType, events after and events before time accordingly. Leaving the query string blank will result
     in all available events being sent.


     Returns: A json object that has only 1 parameter, result which is an array of all event logs that fits the
     criteria listed.
    """
    requested_id = request.args.get('userId')
    start_time = None
    end_time = None
    if request.args.get('startTime'):
        start_time = parser.parse(request.args.get('startTime'))
    if request.args.get('endTime'):
        end_time = parser.parse(request.args.get('endTime'))
    log_type = request.args.get('type')

    query = db.session.query(Log, Actions).filter(Actions.log_id == Log.log_id)

    if requested_id:
        query = query.filter(Log.user_id == requested_id)

    if start_time:
        query = query.filter(Actions.time >= start_time)

    if end_time:
        query = query.filter(Actions.time <= end_time)

    if log_type:
        query = query.filter(Actions.action_type == log_type)

    result = query.all()

    log_list = []

    for row in result:
        report_row = {
            'userId': row[0].user_id,
            'sessionId': row[0].session_id,
            'time': str(row[1].time),
            'type': row[1].action_type,
            'properties': json.loads(row[1].properties)
        }

        log_list.append(report_row)

    return json.dumps(dict(result = log_list)), 200, {'Content-Type': 'application/json'}


if __name__ == "__main__":
    app.run(debug=True)
