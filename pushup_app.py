import time
import threading
import cv2
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tensorflow import keras
import matplotlib.pyplot as plt
import os, shutil
import PoseModule as pm
from utils import Button, Label
from PIL import Image, ImageTk

Tk().withdraw()

model_up = keras.models.load_model("models/push_up_loss.h5")
model_down = keras.models.load_model("models/push_up_down.h5")

def preprocessing_image(img):
    img = cv2.resize(img, dsize=(224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.reshape(1, 224, 224, 3)
    return img

def preprocessing_image2(img):
    img = cv2.resize(img, dsize=(336, 336))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.reshape(1, 336, 336, 3)
    return img

test_img = cv2.imread("sample_images/img1.jpg")
predict_test_image = preprocessing_image(test_img)
model_up.predict(predict_test_image)
model_down.predict(predict_test_image)

WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 720
VIDEO_X, VIDEO_Y = 25, 45
scale_rate = 1.4
VIDEO_WIDTH, VIDEO_HEIGHT = int(576 * scale_rate), int(320 * scale_rate)

bg = np.ones((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype="uint8")*111
bg = cv2.rectangle(bg, (VIDEO_X-2, VIDEO_Y-2), (VIDEO_X + VIDEO_WIDTH+2, VIDEO_Y + VIDEO_HEIGHT+2), (255, 255, 255), 2)
bg[VIDEO_Y:VIDEO_Y+VIDEO_HEIGHT, VIDEO_X:VIDEO_X+VIDEO_WIDTH] = np.ones((VIDEO_HEIGHT, VIDEO_WIDTH, 3), dtype="uint8")*137


# Draw Bar
bar_height = 325

global check
global per_left
global bar_left
global per_right
global bar_right

lb_title = Label("PUSH-UP EVALUATION", 300, (45, 0), (700, 40), (255, 255, 0), 1, 3, None)
# lb_title.config(font=("Transformers Movie", 50))

play_thread = None
# Variable to detect landmarks and predict
count, no_right, no_wrong = 0, 0, 0
fps = 0

up_list, down_list = [], []

angle_list, filter_list = [], []
eval = False

running = True

def play_video(video_path, x, y, width, height):
    global bg, running, btn_list
    global count, no_right, no_wrong, fps, up_list, down_list
    global angle_list, filter_list, eval
    global color_tmp
    color_tmp = (255, 0, 255)
    count, no_right, no_wrong = 0, 0, 0
    detector = pm.poseDetector()

    angle_list = [160]
    filter_list = [140]

    frame_count = 0
    frame_skip_rate = 6

    T = 50
    beta = 1 - frame_skip_rate / T

    high = True

    up_right = True
    no_right, no_wrong = 0, 0

    up_list = []
    down_list = []

    target_frame, target_angle = None, 0

    cap = cv2.VideoCapture(video_path)
    pTime = 0

    while running:
        success, org_frame = cap.read()
        if not success:
            break

        frame = cv2.resize(org_frame, dsize=(VIDEO_WIDTH, VIDEO_HEIGHT))
        frame = detector.findPose(frame, draw=False)
        lmList = detector.findPosition(frame, draw=False)
    
        if lmList:
            # frame, _ = detector.findBoundingBox(frame, draw=True)
            
            if not detector.left():
                check = 0
                tmp_angle = detector.findAngle(frame, 24, 26, 28, draw=True)
                cur_angle = detector.findAngle(frame, 12, 14, 16, draw=True)
                per = np.interp(cur_angle, (65, 150), (0, 100))
                bar = np.interp(cur_angle, (65, 150), (bar_height, 100))
            else:
                check = 1
                tmp_angle = detector.findAngle(frame, 23, 25, 27, draw=True)
                cur_angle = detector.findAngle(frame, 11, 13, 15, draw=True)
                per = np.interp(cur_angle, (65, 150), (0, 100))
                bar = np.interp(cur_angle, (65, 150), (bar_height, 100))

            if (frame_count + 1) % frame_skip_rate == 0:
                cur_angle = max(60, cur_angle)
                angle_list.append(cur_angle)

                if high and cur_angle > target_angle:
                    target_frame, target_angle = org_frame, cur_angle
                if not high and cur_angle < target_angle:
                    target_frame, target_angle = org_frame, cur_angle

                Fn = beta * filter_list[-1] + (1 - beta) * cur_angle
                filter_list.append(Fn)
                
                if high and Fn > cur_angle:
                    count += 0.5
                    high = False
                    predict_image = preprocessing_image(target_frame)
                    rate = model_up.predict(predict_image)[0][0]
                    if per == 100:
                        color_tmp = (0, 255, 0)
                    if rate < 0.5 and tmp_angle > 160:
                        up_right = True
                        print("Up Right")
                    else:
                        up_right = False
                        print("Up Wrong", rate)

                    up_list.append((target_frame, up_right, rate))

                    target_angle = 200

                if not high and Fn < cur_angle:
                    count += 0.5
                    high = True
                    predict_image = preprocessing_image(target_frame)
                    rate = model_down.predict(predict_image)[0][0]
                    if per == 0:
                        color_tmp = (0, 255, 0)
                    if rate < 0.5 and tmp_angle > 160:
                        down_right = True
                        print("Down Right")
                    else:
                        down_right = False
                        print("Down Wrong", rate)

                    down_list.append((target_frame, down_right, rate))

                    if up_right and down_right:
                        no_right += 1
                    else:
                        no_wrong += 1

                    target_angle = 0

            frame_count += 1
        bar_tmp = 720
        bar_tmp_2 = 758
        bar_tmp_3 = 643
        if check == 0 :
            cv2.rectangle(frame, (bar_tmp, 100), (bar_tmp_2, bar_height), color_tmp, 3)
            cv2.rectangle(frame, (bar_tmp, int(bar)), (bar_tmp_2, bar_height), color_tmp, cv2.FILLED)
            cv2.putText(frame, f'{int(per)} %', (bar_tmp_3, 75), cv2.FONT_HERSHEY_PLAIN, 4,
                        color_tmp, 4)
        else :
            cv2.rectangle(frame, (bar_tmp, 100), (bar_tmp_2, bar_height), color_tmp, 3)
            cv2.rectangle(frame, (bar_tmp, int(bar)), (bar_tmp_2, bar_height), color_tmp, cv2.FILLED)
            cv2.putText(frame, f'{int(per)} %', (bar_tmp_3, bar_tmp), cv2.FONT_HERSHEY_PLAIN, 4,
                        color_tmp, 4)
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        bg[y:y+height, x:x+width] = frame
        cv2.waitKey(1)
    reset_btn(btn_list)
    eval = True

def evaluate(agl_list, fil_list, u_list, d_list):
    plt.figure(figsize=(10, 10))
    plt.plot(agl_list)
    plt.plot(fil_list)
    plt.show()

    l = len(d_list)
    color = {"RIGHT" : (0, 255, 0),
             "WRONG": (0, 0, 255)}

    for i in range(l):
        up_img, up_right, up_rate = u_list[i]
        down_img, down_right, down_rate = d_list[i]

        up_img = cv2.resize(up_img, dsize=(600, 400))
        down_img = cv2.resize(down_img, dsize=(600, 400))
        up_str = "RIGHT" if up_right else "WRONG"
        down_str = "RIGHT" if down_right else "WRONG"


        ver = np.concatenate((up_img, down_img), axis=0)
        ver = cv2.putText(ver, up_str, (50, 50), cv2.FONT_HERSHEY_PLAIN, 3, color[up_str], 3)
        ver = cv2.putText(ver, str(up_rate), (50, 100), cv2.FONT_HERSHEY_PLAIN, 3, color[up_str], 3)
        ver = cv2.putText(ver, down_str, (50, 450), cv2.FONT_HERSHEY_PLAIN, 3, color[down_str], 3)
        ver = cv2.putText(ver, str(down_rate), (50, 500), cv2.FONT_HERSHEY_PLAIN, 3, color[down_str], 3)
        
        
        
        lastname = f'{i}/{l}'
        cv2.destroyWindow(lastname)

        cur_name = f'{i+1}/{l}'
        cv2.namedWindow(cur_name)
        cv2.moveWindow(cur_name, 500, 90)
        cv2.imshow(cur_name, ver)
        cv2.waitKey(0)
    
def video_player(file_name):
    global running, play_thread, eval
    if eval:
        return

    running = False
    if play_thread:
        play_thread.join()

    running = True
    play_thread = threading.Thread(target=play_video, args=(file_name, VIDEO_X, VIDEO_Y, VIDEO_WIDTH, VIDEO_HEIGHT))
    play_thread.start()

def btn_file_action():
    file_name = askopenfilename()
    file_name = file_name.replace("/", "//")
    video_player(file_name)

def btn_camera_action():
    video_player(0)

def btn_stop_action():
    global running
    running = False

quit = False
def btn_quit_action():
    global running, play_thread, quit
    running = False
    if play_thread:
        play_thread.join()
    quit = True
    
btn_x = (WINDOW_WIDTH + VIDEO_X + VIDEO_WIDTH - 80) // 2
btn_file = Button("File (F)", 110, (btn_x, 95), (200, 80), 1, 2, btn_file_action)
btn_camera = Button("Camera (C)", 185, (btn_x, 325), (200, 80), 1, 2, btn_camera_action)
btn_stop = Button("Stop (S)", 120, (btn_x, 210), (200, 80), 1, 2, btn_stop_action)
btn_quit = Button("Quit (Q)", 100, (btn_x, 375), (200, 80), 1, 2, btn_quit_action)

icon_right = ImageTk.PhotoImage(Image.open("icon_image/right_icon.png"))
icon_wrong = ImageTk.PhotoImage(Image.open("icon_image/wrong_icon.png"))
icon_total = ImageTk.PhotoImage(Image.open("icon_image/total_icon.png"))
btn_test = Button(icon_total, 120, (120, 280), (200, 80), 1, 2, None)
lb_y = (WINDOW_HEIGHT + VIDEO_Y + VIDEO_HEIGHT - 50) // 2

lb_total = Label("TOTAL: 0", 100, (545, lb_y), (200, 50), (255, 0, 255), 1, 3, None)
lb_right = Label("RIGHT: 0", 100, (45, lb_y), (200, 50), (0, 255, 0), 1, 3, None)
lb_wrong = Label("WRONG: 0", 100, (245, lb_y), (200, 50), (0, 0, 255), 1, 3, None)
lb_fps = Label(f"fps: {str(int(fps))}", 100, (WINDOW_WIDTH-175, WINDOW_HEIGHT-50), (175, 50), (255, 255, 255), 1, 3, None)

btn_list = [btn_file, btn_camera, btn_stop]
utils = [lb_title, btn_file, btn_camera, btn_stop, lb_total, lb_right, lb_wrong, lb_fps]

def reset_btn(list_of_btn):
    for btn in list_of_btn:
        btn.set_state(0)

def mouse_click(event, x, y, flags, param):
    global btn_list

    # mouse hover
    for btn in btn_list:
        if btn.mouse_focus(x, y) and btn.get_state() != 2:
            btn.set_state(1)
        elif btn.get_state() == 1:
            btn.set_state(0)

    # mouse clicked
    if event == cv2.EVENT_LBUTTONDBLCLK:
        for btn in btn_list:
            if btn.mouse_focus(x, y):
                reset_btn(btn_list)
                btn.set_state(2)
                btn.call_func()


cv2.namedWindow("Push-up Recognition")
cv2.setMouseCallback("Push-up Recognition", mouse_click)

image_path = "icon_image//background.png"
my_bgr = cv2.imread(image_path, 1)
while not quit:
    bg[lb_y: , ] = np.ones((WINDOW_HEIGHT-lb_y, WINDOW_WIDTH, 3), dtype="uint8")*111

    for util in utils:
        bg = util.place(bg)

    cv2.imshow("Push-up Recognition", bg)

    lb_total.set_text(f"TOTAL: {str(int(count))}")
    lb_right.set_text(f"RIGHT: {str(no_right)}")
    lb_wrong.set_text(f"WRONG: {str(no_wrong)}")
    lb_fps.set_text(f"fps: {str(int(fps))}")

    key = cv2.waitKey(1) & 0xFF
    if eval:
        evaluate(angle_list, filter_list, up_list, down_list)
        eval = False

    if key == ord('q') or quit:
        break

    elif key == ord('f'):
        btn_file.set_state(2)
        btn_file.call_func()

    elif key == ord('c'):
        btn_camera.set_state(2)
        btn_camera.call_func()

    elif key == ord('s'):
        btn_stop.set_state(2)
        btn_stop.call_func()

running = False
cv2.destroyAllWindows()
