from datetime import datetime
from dateutil import parser

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
    package = request.get_json()
    current_log = Log(user_id=package['userId'], session_id=package['sessionId'])
    db.session.add(current_log)
    for action in package['actions']:
        action = Actions(
            properties=str(action['properties']),
            action_type=action['type'],
            time=parser.parse(action['time']),
            log=current_log)
        db.session.add(action)

    db.session.commit()

    return 'log'


if __name__ == "__main__":
    app.run(debug=True)
