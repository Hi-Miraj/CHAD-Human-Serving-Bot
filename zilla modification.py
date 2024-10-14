import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import serial
import time

# Load Firebase service account credentials
cred = credentials.Certificate('face-detection-31d91-firebase-adminsdk-89zyu-2ab2461b00.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://face-detection-31d91-default-rtdb.firebaseio.com/'
})

# Initialize Firebase Realtime Database reference
ref = db.reference('attendance')

# Load images and class names
path = 'images'
images = []
classNames = []
myList = os.listdir(path)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

# Encode known faces
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(images)
print('Encoding Complete')


# Initialize webcam
cap = cv2.VideoCapture(1)

# Initialize serial communication with Arduino
ser = serial.Serial('COM4', 9600, timeout=1)

# Variables to track detections and time
detection_start_time = 0
detected_name = None

# Process webcam frames
while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y2), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            # Mark attendance in Firebase Realtime Database
            attendance_ref = ref.child('attendance')
            if not attendance_ref.child(name).get():
                now = datetime.now()
                dtString = now.strftime('%H:%M:%S')
                attendance_ref.child(name).set(dtString)

            # Detect 'Guilty.jpg' and continuously send 'T' to Arduino for 1.5 seconds
            if name == 'ELON MUSK(DENGUE POSITIVE)' and detected_name != 'ELON MUSK(DENGUE POSITIVE)':
                detection_start_time = time.time()
                detected_name = 'ELON MUSK(DENGUE POSITIVE)'

        else:
            # Unrecognized face, assign an ID
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y2), (x2, y2), (0, 0, 255), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 0, 255), cv2.FILLED)
            cv2.putText(img, 'Unknown', (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            # Assign an ID and mark attendance in Firebase Realtime Database
            attendance_ref = ref.child('attendance')
            values = attendance_ref.get().values()
            int_values = [int(val) for val in values if val.isdigit()]
            max_id = max(int_values) if int_values else 0
            new_id = max_id + 1
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            attendance_ref.child(f'ID_{new_id}').set(dtString)

            # Continuously send 'O' to Arduino for 1.5 seconds (except for 'Guilty.jpg')
            if detected_name != 'UNKNOWN':
                detection_start_time = time.time()
                detected_name = 'UNKNOWN'

    # Continuously send 'O' or 'T' to Arduino based on detections
    if time.time() - detection_start_time < 1.5:
        if detected_name == 'ELON MUSK(DENGUE POSITIVE)':
            ser.write(b'T')  # Send 'T' to Arduino
        else:
            ser.write(b'O')  # Send 'O' to Arduino
    else:
        ser.write(b'G')  # Send 'G' to Arduino when no detection occurs

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()
