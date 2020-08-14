import json
import unittest

from app import Log, Actions
from flask_sqlalchemy import SQLAlchemy

from app import app, db


class TestCase(unittest.TestCase):
    def setUp(self) -> None:
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        # db.session.remove()
        # db.drop_all()
        return None

    def test_posting_valid_data(self):
        response = self.app.post('/log',
                                 content_type='application/json',
                                 data=json.dumps(
                                     dict(
                                         userId='user1',
                                         sessionId='session1',
                                         actions=[
                                             dict(
                                                 time="2018-10-18T21:37:28-06:00",
                                                 type="CLICK",
                                                 properties={
                                                     "locationX": 52,
                                                     "locationY": 11
                                                 }
                                             ),
                                             dict(
                                                 time="2018-10-18T21:37:28-06:00",
                                                 type="VIEW",
                                                 properties={
                                                     "viewID": 'IDViewed'
                                                 }
                                             )
                                         ]
                                     )
                                 )
                                 )

        self.assertEqual(response.status_code, 200)

    def test_posting_invalid_time(self):
        response = self.app.post('/log',
                                 content_type='application/json',
                                 data=json.dumps(
                                     dict(
                                         userId='user2',
                                         sessionId='session2',
                                         actions=[
                                             dict(
                                                 time="Not a time",
                                                 type="CLICK",
                                                 properties={
                                                     "locationX": 52,
                                                     "locationY": 11
                                                 }
                                             )
                                         ]
                                     )
                                 )
                                 )

        self.assertEqual(response.status_code, 400)

    def test_posting_missing_user(self):
        response = self.app.post('/log',
                                 content_type='application/json',
                                 data=json.dumps(
                                     dict(
                                         sessionId='sessionDNE',
                                         actions=[
                                             dict(
                                                 time="2018-10-18T21:37:28-06:00",
                                                 type="CLICK",
                                                 properties={
                                                     "locationX": 52,
                                                     "locationY": 11
                                                 }
                                             )
                                         ]
                                     )
                                 )
                                 )

        self.assertEqual(response.status_code, 400)

    def test_posting_missing_session(self):
        response = self.app.post('/log',
                                 content_type='application/json',
                                 data=json.dumps(
                                     dict(
                                         userId='user1',
                                         actions=[
                                             dict(
                                                 time="2018-10-18T21:37:28-06:00",
                                                 type="CLICK",
                                                 properties={
                                                     "locationX": 52,
                                                     "locationY": 11
                                                 }
                                             )
                                         ]
                                     )
                                 )
                                 )

        self.assertEqual(response.status_code, 400)

    def test_post_data_then_generate_report(self):
        # generate test data
        response = self.app.post('/log',
                                 content_type='application/json',
                                 data=json.dumps(
                                     dict(
                                         userId='testuser1',
                                         sessionId='testsession1',
                                         actions=[
                                             dict(
                                                 time="2020-01-01T21:37:28-06:00",
                                                 type="CLICK",
                                                 properties={
                                                     "locationX": 52,
                                                     "locationY": 11
                                                 }
                                             ),
                                             dict(
                                                 time="2018-10-18T21:37:28-06:00",
                                                 type="VIEW",
                                                 properties={
                                                     "viewID": 'IDViewed'
                                                 }
                                             ),
                                         ]
                                     )
                                 )
                                 )
        self.assertEqual(response.status_code, 200)

        response = self.app.post('/log',
                                 content_type='application/json',
                                 data=json.dumps(
                                     dict(
                                         userId='testuser1',
                                         sessionId='testsession2',
                                         actions=[
                                             dict(
                                                 time="2019-01-01T21:37:28-06:00",
                                                 type="CLICK",
                                                 properties={
                                                     "locationX": 52,
                                                     "locationY": 11
                                                 }
                                             ),
                                             dict(
                                                 time="2018-10-18T21:37:28-06:00",
                                                 type="VIEW",
                                                 properties={
                                                     "viewID": 'IDViewed'
                                                 }
                                             ),
                                         ]
                                     )
                                 )
                                 )
        self.assertEqual(response.status_code, 200)

        response = self.app.post('/log',
                                 content_type='application/json',
                                 data=json.dumps(
                                     dict(
                                         userId='testuser2',
                                         sessionId='testsession2',
                                         actions=[
                                             dict(
                                                 time="2019-01-01T21:37:28-06:00",
                                                 type="CLICK",
                                                 properties={
                                                     "locationX": 52,
                                                     "locationY": 11
                                                 }
                                             ),
                                             dict(
                                                 time="2018-10-18T21:37:28-06:00",
                                                 type="VIEW",
                                                 properties={
                                                     "viewID": 'IDViewed'
                                                 }
                                             ),
                                         ]
                                     )
                                 )
                                 )
        self.assertEqual(response.status_code, 200)

        response = self.app.get('/log')
        self.assertEqual(response.status_code, 200)

        self.assertIsNotNone(response.get_json)

        # Test filter by user
        response = self.app.get('/log?userId=testuser1')
        result = response.get_json()
        self.assertEqual(len(result['result']), 4)

        # Test filter by type
        response = self.app.get('/log?userId=testuser1&type=CLICK')
        result = response.get_json()
        print(result)
        self.assertEqual(len(result['result']), 2)

        # Test filter by start time
        response = self.app.get('/log?userId=testuser1&startTime=2019-01-02T21:37:28-06:00')
        result = response.get_json()
        self.assertEqual(len(result['result']), 1)

        # Test filter by endTime
        response = self.app.get('/log?endTime=2018-01-19T21:37:28-06:00')
        result = response.get_json()
        self.assertEqual(len(result['result']), 0)

        # Test filter by between time
        response = self.app.get('/log?userId=testuser1&startTime=2018-10-19T21:37:28-06:00&endTime=2019-10-18T21:37:28'
                                '-06:00')
        result = response.get_json()
        self.assertEqual(len(result['result']), 1)


if __name__ == '__main__':
    unittest.main()
