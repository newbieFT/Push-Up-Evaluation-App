import numpy as np
import cv2
import os, shutil
import PoseModule as pm
import time

samples_path = "sample_videos"

video = "test2.mp4"
cap = cv2.VideoCapture(samples_path + "/" + video)

cur_left_angle = 0
prev_left_angle = 90
prev_right_angle = 90
degree_up = False
count = 0
frame_count = 0
pTime = 0

detector = pm.poseDetector()

while True:
    # Capture frame-by-frame
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.resize(frame, dsize=(1080, 720))

    frame = detector.findPose(frame, draw=False)
    lmList = detector.findPosition(frame, draw=False)
    if lmList:
        # Our operations on the frame come here
        mouth_left, mouth_right = lmList[9][2], lmList[10][2]
        shoulder_left, shoulder_right = lmList[11][2], lmList[12][2]
        cv2.circle(frame, (lmList[9][1], lmList[9][2]), 10, (0, 255, 0), 2)
        cv2.circle(frame, (lmList[10][1], lmList[10][2]), 10, (0, 255, 0), 2)
        cv2.circle(frame, (lmList[11][1], lmList[11][2]), 10, (0, 255, 0), 2)
        cv2.circle(frame, (lmList[12][1], lmList[12][2]), 10, (0, 255, 0), 2)
        print(lmList[11], lmList[12])

        cur_left_angle = detector.findAngle(frame, 11, 13, 15, draw=True)
        cur_right_angle = detector.findAngle(frame, 12, 14, 16, draw=True)
        if frame_count % 5 == 0:
            if degree_up:
                if ((cur_left_angle < prev_left_angle) and (90 < cur_left_angle < 190)) or ((cur_right_angle < prev_right_angle) and (90 < cur_right_angle < 190)):
                    count += 0.5
                    degree_up = False
            elif mouth_left + mouth_right >= shoulder_left + shoulder_right:
                if ((cur_left_angle > prev_left_angle) and (0 < cur_left_angle < 140)) or ((cur_right_angle > prev_right_angle) and (0 < cur_right_angle < 140)):
                    count += 0.5
                    degree_up = True
            prev_left_angle = cur_left_angle
            prev_right_angle = cur_right_angle

        frame_count += 1

    cv2.putText(frame, str(int(count)), (70, 600), cv2.FONT_HERSHEY_PLAIN, 15, (0, 0, 255), 2)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(frame, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)



    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()