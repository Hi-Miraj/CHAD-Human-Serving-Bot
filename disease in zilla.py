import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import ttk
import serial
import time

# Replace 'COM3' with the appropriate serial port for your Arduino
ARDUINO_PORT = 'COM4'
ARDUINO_BAUDRATE = 9600

path = 'image query'
orb = cv2.ORB_create(nfeatures=1000)

#### Import images
images = []
classNames = []
myList = os.listdir(path)
print(myList)
print('Total Classes Detected', len(myList))
for cl in myList:
    imgcur = cv2.imread(f'{path}/{cl}', 0)
    images.append(imgcur)
    classNames.append((os.path.splitext(cl)[0]))
print(classNames)

def findDes(imaged):
    desList = []
    for img in images:
        kp, des = orb.detectAndCompute(img, None)
        desList.append(des)
    return desList

def findID(img, desList, thres=15):
    kp2, des2 = orb.detectAndCompute(img, None)
    bf = cv2.BFMatcher()
    matchList = []
    finalval = -1
    try:
        for des in desList:
            matches = bf.knnMatch(des, des2, k=2)
            good = []
            for m, n in matches:
                if m.distance < 0.75 * n.distance:
                    good.append([m])

            matchList.append(len(good))
    except:
        pass

    if len(matchList) != 0:
        if max(matchList) > thres:
            finalval = matchList.index(max(matchList))
    return finalval

desList = findDes(images)
print(len(desList))

# Disease descriptions and treatments
disease_info = {
    'Rosacea[diagnosed]T-491': {
        'description': 'Rosacea is a long-term skin condition that typically affects the face. It causes redness, visible blood vessels, and sometimes pimples and bumps.',
        'treatment': 'Treatment for rosacea may involve topical medications, oral antibiotics, laser therapy, and lifestyle changes like avoiding triggers and protecting the skin from sun exposure.',
    },
    'Rosacea[diagnosed]T-492': {
        'description': 'Rosacea is a long-term skin condition that typically affects the face. It causes redness, visible blood vessels, and sometimes pimples and bumps.',
        'treatment': 'Treatment for rosacea may involve topical medications, oral antibiotics, laser therapy, and lifestyle changes like avoiding triggers and protecting the skin from sun exposure.',
    },
    'Rosacea[diagnosed]T-493': {
        'description': 'Rosacea is a long-term skin condition that typically affects the face. It causes redness, visible blood vessels, and sometimes pimples and bumps.',
        'treatment': 'Treatment for rosacea may involve topical medications, oral antibiotics, laser therapy, and lifestyle changes like avoiding triggers and protecting the skin from sun exposure.',
    },
    'Fractured Finger[Diagnosed]T-393' : {
        'description': 'A fractured finger refers to a break or crack in one or more of the bones of the finger. It typically results from trauma or excessive force applied to the finger. Symptoms include pain, swelling, and difficulty in moving or using the finger. Prompt medical attention and appropriate treatment are necessary for proper healing and to avoid potential complications.',
        'treatment': 'The treatment for a fractured finger usually involves immobilization with a splint or cast to promote healing, along with pain management techniques. In some cases, surgical intervention may be required for more severe fractures.',
    }

    # Add more diseases and their information as needed
}

# Create a new Tkinter window
window = tk.Tk()
window.title('Disease Detection')
window.geometry('800x600')

# Initialize serial communication with Arduino
ser = serial.Serial(ARDUINO_PORT, ARDUINO_BAUDRATE, timeout=1)

# Create a tabbed interface
tab_control = ttk.Notebook(window)
tab_detection = ttk.Frame(tab_control)
tab_information = ttk.Frame(tab_control)

tab_control.add(tab_detection, text='Disease Detection')
tab_control.add(tab_information, text='Disease Information')
tab_control.pack(expand=True, fill='both')

# Create labels for disease description and treatment
description_label = tk.Label(tab_information, text='Description:', font=('Arial', 12, 'bold'))
description_label.pack(pady=10)
description_text = tk.Text(tab_information, height=10, width=80)
description_text.pack()

treatment_label = tk.Label(tab_information, text='Treatment:', font=('Arial', 12, 'bold'))
treatment_label.pack(pady=10)
treatment_text = tk.Text(tab_information, height=10, width=80)
treatment_text.pack()

def update_information(disease_name):
    if disease_name in disease_info:
        disease = disease_info[disease_name]
        description_text.delete('1.0', 'end')
        description_text.insert('end', disease['description'])

        treatment_text.delete('1.0', 'end')
        treatment_text.insert('end', disease['treatment'])

cap = cv2.VideoCapture(1)  # Use 0 for the default camera
disease_detected = False  # Initialize the disease detection status
disease_detected_time = 0  # Initialize the time when the disease was first detected

def send_command_to_arduino(command):
    ser.write(command.encode())  # Convert the command to bytes and send it to Arduino

def show_frame():
    global disease_detected, disease_detected_time
    success, img2 = cap.read()
    imgOrignal = img2.copy()
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    id = findID(img2, desList)
    if id != -1:
        cv2.putText(imgOrignal, classNames[id], (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)

        # Check if disease is detected continuously for more than 1.5 seconds
        if not disease_detected:
            disease_detected = True
            disease_detected_time = time.time()
        elif time.time() - disease_detected_time > 0.5:
            # Update information and send 'R' command only if detected for more than 1.5 seconds
            update_information(classNames[id])
            send_command_to_arduino('R')
    else:
        disease_detected = False  # Reset the disease detection status
        # Send 'G' command to Arduino if no disease is detected
        send_command_to_arduino('G')

    cv2.imshow('img2', imgOrignal)
    if cv2.waitKey(1) == ord('q'):
        window.quit()
        return

    window.after(10, show_frame)

window.after(10, show_frame)
window.mainloop()

cap.release()
cv2.destroyAllWindows()
