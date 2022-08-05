import numpy as np
import cv2
import os, shutil
import PoseModule as pm


# Delete all file in directory (if needed)
def delete_all_file(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

path = 'test_output_frames'
delete_all_file(path + "/up")
delete_all_file(path + "/down")

samples_path = "test_sample_videos"
destination_path = "test_output_frames"

total = 1
frame_index = 1
frame_count = 0
cur_left_angle, cur_right_angle = 0, 0
prev_left_angle, prev_right_angle = 90, 90
degree_up = False

for video in os.listdir(samples_path):
    cap = cv2.VideoCapture(samples_path + "/" + video)

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

            mouth_left, mouth_right = lmList[9][2], lmList[10][2]
            shoulder_left, shoulder_right = lmList[11][2], lmList[12][2]

            if frame_count % 5 == 0:
                cur_left_angle = detector.findAngle(frame, 11, 13, 15, draw=False)
                cur_right_angle = detector.findAngle(frame, 12, 14, 16, draw=False)
                if degree_up:
                    if ((cur_left_angle < prev_left_angle) and (90 < cur_left_angle < 190)) or ((cur_right_angle < prev_right_angle) and (90 < cur_right_angle < 190)):
                        degree_up = False
                        cv2.imwrite(destination_path + "/up/frame" + str(frame_index) + ".png", frame)
                        frame_index += 1
                elif mouth_left + mouth_right >= shoulder_left + shoulder_right:
                    if ((cur_left_angle > prev_left_angle) and (0 < cur_left_angle < 140)) or ((cur_right_angle > prev_right_angle) and (0 < cur_right_angle < 140)):
                        degree_up = True
                        cv2.imwrite(destination_path + "/down/frame" + str(frame_index) + ".png", frame)
                        frame_index += 1
                prev_left_angle = cur_left_angle

            frame_count += 1

        # Display the resulting frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()