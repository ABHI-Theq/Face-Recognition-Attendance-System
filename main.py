import os
import pickle
import cv2
import face_recognition
import cvzone
import numpy as np
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, storage
from firebase_admin import db


class FaceAttendanceSystem:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.img_bg = cv2.imread('Resources/background.png')
        self.folder_mode_path = 'Resources/Modes'
        self.mode_type = 0
        self.counter = 0
        self.id = -1
        self.img_student = []
        self.encode_list_known = []
        self.student_ids = []
        self.TIME_DURATION=30
        # Initialize Firebase
        self.init_firebase()

        # Load encoding file
        self.load_encoding_file()

        # Load mode images
        self.load_mode_images()

    def init_firebase(self):
        cred = credentials.Certificate("serviceAccountKeyACCOuntTYPE.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'DATABASE_URL',
            'storageBucket': 'DATABASE_STORAGE'
        })
        self.bucket = storage.bucket()

    def load_encoding_file(self):
        print("Loading Encode File ...")
        with open('EncodingFile.p', 'rb') as file:
            encode_list_known_with_ids = pickle.load(file)
            self.encode_list_known, self.student_ids = encode_list_known_with_ids
        print("Encode File Loaded")

    def load_mode_images(self):
        mode_path_list = os.listdir(self.folder_mode_path)
        self.img_mode_list = [cv2.imread(os.path.join(self.folder_mode_path, path)) for path in mode_path_list]

    def run(self):
        while True:
            success, img = self.cap.read()
            img_s = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            img_s = cv2.cvtColor(img_s, cv2.COLOR_BGR2RGB)

            face_cur_frame = face_recognition.face_locations(img_s)
            encode_cur_frame = face_recognition.face_encodings(img_s, face_cur_frame)

            self.img_bg[162:162 + 480, 55:55 + 640] = img
            self.img_bg[44:44 + 633, 808:808 + 414] = self.img_mode_list[self.mode_type]

            if face_cur_frame:
                for encode_face, face_loc in zip(encode_cur_frame, face_cur_frame):
                    matches = face_recognition.compare_faces(self.encode_list_known, encode_face)
                    face_dis = face_recognition.face_distance(self.encode_list_known, encode_face)
                    match_index = np.argmin(face_dis)

                    if matches[match_index]:
                        y1, x2, y2, x1 = face_loc
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                        bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                        self.img_bg = cvzone.cornerRect(self.img_bg, bbox, rt=0)
                        self.id = self.student_ids[match_index]
                        if self.counter == 0:
                            cvzone.putTextRect(self.img_bg, "Loading", (275, 400))
                            cv2.imshow("Face Attendance", self.img_bg)
                            cv2.waitKey(1)
                            self.counter = 1
                            self.mode_type = 1

                if self.counter != 0:
                    if self.counter == 1:
                        self.process_attendance()

                    if self.mode_type != 3:
                        if 10 < self.counter < 20:
                            self.mode_type = 2

                        self.img_bg[44:44 + 633, 808:808 + 414] = self.img_mode_list[self.mode_type]

                        if self.counter <= 10:
                            self.update_info_on_image()

                        self.counter += 1

                        if self.counter >= 30:
                            self.reset_counter()

            else:
                self.mode_type = 0
                self.counter = 0

            cv2.imshow("Face Attendance", self.img_bg)
            cv2.waitKey(1)

    def process_attendance(self):
        student_info = db.reference(f'Students/{self.id}').get()
        blob = self.bucket.get_blob(f'Images/{self.id}.png')
        array = np.frombuffer(blob.download_as_string(), np.uint8)
        self.img_student = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

        datetime_object = datetime.strptime(student_info['last_attendanceTime'], "%Y-%m-%d %H:%M:%S")
        seconds_elapsed = (datetime.now() - datetime_object).total_seconds()

        if seconds_elapsed > 30:
            ref = db.reference(f'Students/{self.id}')
            student_info['total_attendance'] += 1
            ref.child('total_attendance').set(student_info['total_attendance'])
            ref.child('last_attendanceTime').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            self.mode_type = 3
            self.counter = 0
            self.img_bg[44:44 + 633, 808:808 + 414] = self.img_mode_list[self.mode_type]

    def update_info_on_image(self):
        studentInfo = db.reference(f'Students/{self.id}').get()

        cv2.putText(self.img_bg, str(studentInfo['total_attendance']), (861, 125),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

        cv2.putText(self.img_bg, str(studentInfo['major']), (1006, 550),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(self.img_bg, str(self.id), (1006, 493),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(self.img_bg, str(studentInfo['standing']), (910, 625),
                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
        cv2.putText(self.img_bg, str(studentInfo['year']), (1025, 625),
                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
        cv2.putText(self.img_bg, str(studentInfo['starting_Year']), (1125, 625),
                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

        (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
        offset = (414 - w) // 2
        cv2.putText(self.img_bg, str(studentInfo['name']), (808 + offset, 445),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

        self.img_bg[175:175 + 216, 909:909 + 216] = self.img_student
        # Add other info here...

    def reset_counter(self):
        self.counter = 0
        self.mode_type = 0
        self.student_info = []
        self.img_student = []
        self.img_bg[44:44 + 633, 808:808 + 414] = self.img_mode_list[self.mode_type]


if __name__ == "__main__":
    attendance_system = FaceAttendanceSystem()
    attendance_system.run()
