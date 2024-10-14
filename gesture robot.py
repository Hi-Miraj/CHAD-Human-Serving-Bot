

import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.SerialModule import SerialObject
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8, maxHands=2)
arduino = SerialObject('COM3')
while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)


    if hands:
       hand2 = hands[0]
       handType2 = hand2["type"]

       finger2 = detector.fingersUp(hand2)

       print(finger2)
       arduino.sendData(finger2)
       #if len(hands)==2:
            #hand1 = hands[1]
            #handType1 = hand1["type"]
            #finger1 = detector.fingersUp(hand1)
    cv2.imshow("Image", img)
    cv2.waitKey(1)