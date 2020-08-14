# Backend coding excercise

Flask server that will accept event logs from the front and and store them in a database as well as
processes allows users to retrieve said event logs based on criterias such as event time, operation and user.

All required libraries are included requirements.txt

To set up the database schema use:
>python setup.py

launch server afterwards using:
>python app.py

to run tests:
>python test_app.py


## Api documentation

**URL**
`/log`

* **Method:** 
 `POST`
 
* **Required Parameters:**
   `userId=[String]`
   `sessionId=[String]`

* **Optional Parameters:**
   `actions=[Array of actions]`
   
* **Sample Request CURL:**

`curl -X POST -H 'Content-Type: application/json' -i 'http://127.0.0.1:5000/log' --data '{
  "userId": "ABC12312XYZ",
  "sessionId": "XYZ45126ABC",
  "actions": [
    {
      "time": "2013-10-18T21:37:28-06:00",
      "type": "CLICK",
      "properties": {
        "locationX": 52,
        "locationY": 11
      }
    },
    {
      "time": "2018-10-18T21:37:30-06:00",
      "type": "VIEW",
      "properties": {
        "viewedId": "FDJKLHSLD"
      }
    },
    {
      "time": "2018-10-18T21:37:30-06:00",
      "type": "NAVIGATE",
      "properties": {
        "pageFrom": "communities",
        "pageTo": "inventory"
      }
    }
  ]
}
'`

* **Result:**
`application/json`

* **Possible Responses:**
>200 Successful

>400 Bad Request
   
   
**URL**
`/log`

* **Method:** 
 `GET`
 
* **Required Parameters:**
    `None`

* **Optional Parameters:**
   `userId(query)=[String], startTime(query)=[String], endTime(query)=[String], type(query)=[String]`

* **Sample Request URL**
    `http://127.0.0.1:5000/log?userId=user1&type=CLICK`

* **Result:**
`application/json`

* **Possible Responses:**
>200 Successful

>400 Bad Request
   
   
## Scalability

The program as of right now scales poorly and would benefit little from being deployed
on the cloud simply due to the limitations of SQLite which is scales poorly because it is limited to 1 writer at a time.
According to the the SQLite developer's when to use SQLite page, SQLite is fine forsites that gets less than 100 thousand clicks per day
, which is more than the requirement of this exercise, but to make this more cloud friendly and easier to scale,
I would transition to a server based database such as deploying a MySQL instance on Amazon RDS in both
development environment as well as production environment.
