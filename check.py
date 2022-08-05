import cv2
import numpy as np
import time
import PoseModule as pm

cap = cv2.VideoCapture("test2.mp4")
img = cv2.imread("rightform.jpg")
detector = pm.poseDetector()

while True:
    # success, img = cap.read()
    # img = cv2.resize(img, (1288, 720))
    img = detector.findPose(img)
    cv2.imshow("Image", img)
    cv2.waitKey(1)