import cv2
import face_recognition
from numpy import load
import numpy as np
from Home.models import attendanceEntry, Present
import datetime
# from datetime import datetime
from django.db.utils import IntegrityError
from django.contrib.auth.models import User

from Home.utils import *

class VideoCamera(object):
    def __init__(self, mode):
        self.video = cv2.VideoCapture(0)
        self.mode = mode

    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret, frame = self.video.read()
        frame = cv2.flip(frame, 1)

        known_face_encodings = load('media/known_face_encodings.npy', allow_pickle=True)
        known_face_names = load('media/known_face_names.npy', allow_pickle=True)

        # DO WHAT YOU WANT WITH TENSORFLOW / KERAS AND OPENCV
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Find all the faces and face encodings in the current frame of video
        cur_face_locations = face_recognition.face_locations(rgb_small_frame)
        cur_face_encodings = face_recognition.face_encodings(
            rgb_small_frame, cur_face_locations)

        face_names = []
        for face_encoding in cur_face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(
                known_face_encodings, face_encoding)

            # Use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(
                known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            print("face distance :", face_distances)
            print("best match index :", face_distances[best_match_index])
            if face_distances[best_match_index] < 0.50:
                name = known_face_names[best_match_index]
                
                # for entry in database                
                if self.mode == 'Entry':
                    update_attendance_in_db_entry(name)                 
                    
                # for exit in database  
                elif self.mode == 'Exit':
                    update_attendance_in_db_exit(name)
                    
            else:
                name = 'Unknown'

            face_names.append(name)

        # Display the results
        for (top, right, bottom, left), name in zip(cur_face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        ret, jpeg = cv2.imencode('.jpg', frame)

        return jpeg.tobytes()
