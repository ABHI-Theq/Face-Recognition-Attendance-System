import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':'https://faceattendancert-389ca-default-rtdb.firebaseio.com/'
})

ref=db.reference('Students')
data={
    "321654":
        {
        "name":"Some Coder",
        "major":"Robotics",
        "starting_Year":2017,
        "total_attendance":6,
        "standing":"6",
        "year":6,
        "last_attendanceTime":"2022-12-11 00:54:34"
    },
"412534":
        {
        "name":"Abhishek-Coding King",
        "major":"Programming",
        "starting_Year":2020,
        "total_attendance":10,
        "standing":"1",
        "year":3,
        "last_attendanceTime":"2023-10-01 10:54:34"
    },
"852741":{
        "name":"Emily Blunt",
        "major":"Eco",
        "starting_Year":2018,
        "total_attendance":4,
        "standing":"2",
        "year":5,
        "last_attendanceTime":"2022-12-21 14:02:34"
    },
"963852":{
        "name":"Elon musk",
        "major":"Entrepreneurship",
        "starting_Year":2016,
        "total_attendance":30,
        "standing":"1",
        "year":7,
        "last_attendanceTime":"2022-12-27 10:24:34"
    },
    "456732": {
        "name": "Deepak Yadav",
        "major": "UPSE Aspirant",
        "starting_Year": 2020,
        "total_attendance": 14,
        "standing": "1",
        "year": 7,
        "last_attendanceTime": "2022-12-27 10:24:34"

    }
}

for key,value in data.items():
    ref.child(key).set(value)
