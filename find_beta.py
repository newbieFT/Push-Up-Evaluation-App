import numpy as np
import cv2
import os, shutil
import PoseModule as pm
import time
import matplotlib.pyplot as plt

samples_path = "sample_videos"
answer_list = [11, 25, 9, 10, 10, 7]

def mse(list1, list2):
    res = 0
    for i in range(len(list1)):
        res += (list1[i] - list2[i]) ** 2
    return res



Ts = [1, 10, 50, 200]
frame_skip_rate_list = [6]

all_counts = [[0 for _ in range(len(Ts))] for _ in range(len(frame_skip_rate_list))]

i_fsr = 0
for frame_skip_rate in frame_skip_rate_list:
    i_T = 0
    for T in Ts:
        count_list = []
        for video in os.listdir(samples_path):
            cap = cv2.VideoCapture(samples_path + "/" + video)

            detector = pm.poseDetector()
            pTime = 0

            angle_list = [160]
            filter_list = [140]

            tmp_list = []

            frame_count = 0

            beta = 1 - frame_skip_rate / T

            high = True
            count = 0

            noi_distance = 6
            high_pivot, low_pivot = - noi_distance, 0

            while True:
                success, org_frame = cap.read()

                if not success:
                    break

                if org_frame.shape[0] > 720 or org_frame.shape[1] > 1080:
                    org_frame = cv2.resize(org_frame, dsize=(1080, 720))

                frame = org_frame.copy()

                frame = detector.findPose(frame, draw=False)
                lmList = detector.findPosition(frame, draw=False)

                if lmList:
                    cur_angle = None
                    if detector.left():
                        cur_angle = detector.findAngle(frame, 11, 13, 15, draw=True)
                    else:
                        cur_angle = detector.findAngle(frame, 12, 14, 16, draw=True)

                    if (frame_count + 1) % frame_skip_rate == 0:
                        cur_angle = max(60, cur_angle)
                        angle_list.append(cur_angle)

                        Fn = beta * filter_list[-1] + (1 - beta) * cur_angle
                        filter_list.append(Fn)

                        if high and Fn < cur_angle:
                            count += 0.5
                            high = False
                        if not high and Fn > cur_angle:
                            count += 0.5
                            high = True
                    frame_count += 1

            count_list.append(int(count))
        all_counts[i_fsr][i_T] = mse(count_list, answer_list)
        i_T += 1
    i_fsr += 1

i_fsr = 0
for fsr in frame_skip_rate_list:
    i_t = 0
    for T in Ts:
        beta = 1 - fsr / T
        print(f"With fsr={fsr}, T={T}, beta={beta}, get MSE: {all_counts[i_fsr][i_t]}")
        i_t += 1
    i_fsr += 1



# T = 50
# fsr = 6
