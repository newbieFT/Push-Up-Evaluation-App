from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import PIL.Image, PIL.ImageTk
from PIL import Image, ImageTk
import time
import threading
import cv2
import numpy as np
import keras
import matplotlib.pyplot as plt
import PoseModule as pm

# Set the interface:
root = Tk()
root.title("Push-Up App")
root.geometry("1200x720")
root.iconbitmap("icon_image/LOGO.ico")

# Set background for app
input_file = Image.open("icon_image/background.png")
bgr = ImageTk.PhotoImage(input_file)
img_window = Label(root, image=bgr)
img_window.place(x=0, y=0)

# Title
main_title = Label(root, text="Push-Up Evaluation", fg="#FFFFFF", bg="#011226", bd=0)
main_title.config(font=("Transformers Movie", 50))
main_title.pack(pady=10)

# Open File Button
button_frame = Frame(root).pack(side=BOTTOM)
icon_file = ImageTk.PhotoImage(Image.open("icon_image/file_icon.png"))
icon_camera = ImageTk.PhotoImage(Image.open("icon_image/camera_icon.png"))
icon_stop = ImageTk.PhotoImage(Image.open("icon_image/stop_icon.png"))
icon_right = ImageTk.PhotoImage(Image.open("icon_image/right_icon.png"))
icon_wrong = ImageTk.PhotoImage(Image.open("icon_image/wrong_icon.png"))
icon_total = ImageTk.PhotoImage(Image.open("icon_image/total_icon.png"))
icon_play = ImageTk.PhotoImage(Image.open("icon_image/resume_icon.png"))
icon_pause = ImageTk.PhotoImage(Image.open("icon_image/pause_icon.png"))

model_up = keras.models.load_model("models/push_up_loss.h5")
model_down = keras.models.load_model("models/push_up_down.h5")
# model_down = keras.models.load_model("models/eff_loss_0714_336x336_B1_down.h5")

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
VIDEO_X, VIDEO_Y = 50, 70
scale_rate = 1.50
VIDEO_WIDTH, VIDEO_HEIGHT = 576, 320

bg = np.ones((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype="uint8")*111
bg = cv2.rectangle(bg, (VIDEO_X-2, VIDEO_Y-2), (VIDEO_X + VIDEO_WIDTH+2, VIDEO_Y + VIDEO_HEIGHT+2), (0, 0, 0), 2)
bg[VIDEO_Y:VIDEO_Y+VIDEO_HEIGHT, VIDEO_X:VIDEO_X+VIDEO_WIDTH] = np.ones((VIDEO_HEIGHT, VIDEO_WIDTH, 3), dtype="uint8")*177
# lb_title = Label("PUSH-UP EVALUATION", 700, (45, 0), (700, 60), (255, 0, 0), 2, 5, None)

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
                cur_angle = detector.findAngle(frame, 12, 14, 16, draw=True)
            else:
                cur_angle = detector.findAngle(frame, 11, 13, 15, draw=True)

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
                    if rate < 0.5:
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
                    if rate < 0.5:
                        down_right = True
                        print("down right")
                    else:
                        down_right = False
                        print("down wrong", rate)

                    down_list.append((target_frame, down_right, rate))

                    if up_right and down_right:
                        no_right += 1
                    else:
                        no_wrong += 1

                    target_angle = 0

            frame_count += 1
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
    color = {"RIGHT" : (255, 0, 0),
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
        cv2.moveWindow(cur_name, 300, 50)
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

def reset_btn(list_of_btn):
    for btn in list_of_btn:
        btn.set_state(0)

def btn_camera_action():
    video_player(0)

def btn_stop_action():
    global running
    running = False
    
# lb_fps = Label(f"fps: {str(int(fps))}", 100, (1200-175, 720-50), (175, 50), (255, 255, 255), 1, 3, None)

class videoGUI :
    
    def __init__(self, window, window_title) :
        
        self.window = window
        self.window.title(window_title)
        
        top_frame = Frame(self.window)
        top_frame.place(x=110, y=150)
        
        bottom_frame = Frame(self.window)
        bottom_frame.place(x=270, y=500)
        
        self.pause = False  # Parameter that controls pause button
        
        self.canvas = Canvas(top_frame, bg="white", height=VIDEO_HEIGHT, width=VIDEO_WIDTH)
        self.canvas.pack()
        
        # Play Button
        self.btn_play = Button(bottom_frame, text="Play  ---", fg="#FFFFFF", bg="#010D1D", borderwidth=5,
                               command=self.play_video)
        self.btn_play.config(font=("Transformers Movie", 10))
        self.play_icon_button = Button(button_frame, image=icon_play, font=("Arial", 30, "bold"), fg="#FFFFFF",
                                       bg="#001E3D", borderwidth=3, command=self.play_video)
        self.play_icon_button.place(x=309, y=504)
        self.btn_play.grid(row=0, column=1)
        
        # Pause Button
        self.btn_pause = Button(bottom_frame, text="Pause    ", fg="#FFFFFF", bg="#010D1D", borderwidth=5,
                                command=self.pause_video)
        self.btn_pause.config(font=("Transformers Movie", 10))
        self.pause_icon_button = Button(button_frame, image=icon_pause, font=("Arial", 30, "bold"), fg="#FFFFFF",
                                        bg="#001E3D", borderwidth=3, command=self.pause_video)
        self.pause_icon_button.place(x=390, y=504)
        self.btn_pause.grid(row=0, column=2)
        
        # Resume Button
        self.btn_resume = Button(bottom_frame, text="Resume    ", fg="#FFFFFF", bg="#010D1D", borderwidth=5,
                                 command=self.resume_video)
        self.btn_resume.config(font=("Transformers Movie", 10))
        self.resume_icon_button = Button(button_frame, image=icon_play, font=("Arial", 30, "bold"), fg="#FFFFFF",
                                         bg="#001E3D", borderwidth=3, command=self.resume_video)
        self.resume_icon_button.place(x=481, y=504)
        self.btn_resume.grid(row=0, column=3)
        
        # Open File Button
        self.file_button = Button(button_frame, text="Open File ---", fg="#FFFFFF", bg="#010D1D", borderwidth=10,
                                  command=self.btn_file_action)
        self.file_button.config(font=("Transformers Movie", 30))
        self.file_icon_button = Button(button_frame, image=icon_file, font=("Arial", 30, "bold"), fg="#FFFFFF",
                                       bg="#001E3D", borderwidth=3, command=self.btn_file_action)
        self.file_icon_button.place(x=1105, y=210)
        self.file_button.place(x=900, y=180)
        
        # Camera Button
        self.camera_button = Button(button_frame, text="Camera ---", fg="#FFFFFF", bg="#010D1D", borderwidth=10,
                                    command=btn_camera_action)
        self.camera_button.config(font=("Transformers Movie", 30))
        self.camera_icon_button = Button(button_frame, image=icon_camera, font=("Arial", 30, "bold"), fg="#FFFFFF",
                                         bg="#001E3D", borderwidth=3, command=btn_camera_action)
        self.camera_icon_button.place(x=1085, y=370)
        self.camera_button.place(x=900, y=340)
        
        # Right push-up
        self.right_button = Button(button_frame, text="   Right:", fg="#7ED114", bg="#010D1D", borderwidth=10)
        self.right_button.config(font=("Transformers Movie", 20))
        self.right_icon_button = Button(button_frame, image=icon_right, font=("Arial", 30, "bold"), fg="#FFFFFF",
                                        bg="#001E3D", borderwidth=3)
        self.right_icon_button.place(x=65, y=623)
        self.right_button.place(x=55, y=610)
        
        # Wrong push-up
        self.wrong_button = Button(button_frame, text="   Wrong:", fg="#F4351B", bg="#010D1D", borderwidth=10)
        self.wrong_button.config(font=("Transformers Movie", 20))
        self.wrong_icon_button = Button(button_frame, image=icon_wrong, font=("Arial", 30, "bold"), fg="#FFFFFF",
                                        bg="#001E3D", borderwidth=3)
        self.wrong_icon_button.place(x=355, y=623)
        self.wrong_button.place(x=345, y=610)
        
        # Total push-up
        self.total_button = Button(button_frame, text="   Total:", fg="#F710E9", bg="#010D1D", borderwidth=10)
        self.total_button.config(font=("Transformers Movie", 20))
        self.total_icon_button = Button(button_frame, image=icon_total, font=("Arial", 30, "bold"), fg="#FFFFFF",
                                        bg="#001E3D", borderwidth=3)
        self.total_icon_button.place(x=655, y=623)
        self.total_button.place(x=645, y=610)
        
        # Stop Button
        self.stop_button = Button(button_frame, text="Stop --", fg="#FFFFFF", bg="#010D1D",
                                  borderwidth=10, command=btn_stop_action)
        self.stop_button.config(font=("Transformers Movie", 30))
        self.stop_icon_button = Button(button_frame, image=icon_stop, font=("Arial", 30, "bold"), fg="#FFFFFF",
                                       bg="#001E3D", borderwidth=3, command=btn_stop_action)
        self.stop_icon_button.place(x=1010, y=527)
        self.stop_button.place(x=900, y=500)
        
        self.delay = 15  # ms
        
        self.window.mainloop()
    
    def btn_file_action(self) :
        
        self.pause = False
        
        self.filename = filedialog.askopenfilename(title="Select file", filetypes=(("MP4 files", "*.mp4"),
                                                                                   ("WMV files", "*.wmv"),
                                                                                ("AVI files", "*.avi")))
        self.filename = self.filename.replace("/", "//")
        video_player(self.filename)
        print(self.filename)
        
        # Open the video file
        self.cap = cv2.VideoCapture(self.filename)
        
        self.width = VIDEO_WIDTH
        self.height = VIDEO_HEIGHT
        
        self.canvas.config(width=self.width, height=self.height)
    
    def get_frame(self) :  # get only one frame
        
        try :
            
            if self.cap.isOpened() :
                ret, frame = self.cap.read()
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        except :
            messagebox.showerror(title='Video file not found', message='Please select a video file.')
    
    def play_video(self) :
        
        # Get a frame from the video source, and go to the next frame automatically
        ret, frame = self.get_frame()
        
        if ret :
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
        
        if not self.pause :
            self.window.after(self.delay, self.play_video)
    
    def pause_video(self) :
        self.pause = True

    # Addition
    def resume_video(self) :
        self.pause = False
        self.play_video()
    
    # Release the video source when the object is destroyed
    def __del__(self) :
        if self.cap.isOpened() :
            self.cap.release()


##### End Class #####

# lb_y = (WINDOW_HEIGHT + VIDEO_Y + VIDEO_HEIGHT - 25) // 2
# lb_total = Label("RIGHT: 0", 100, (45, lb_y), (200, 50), (0, 255, 0), 1, 3, None)
# lb_right = Label("WRONG: 0", 100, (345, lb_y), (200, 50), (0, 255, 255), 1, 3, None)
# lb_wrong = Label("TOTAL: 0", 100, (545, lb_y), (200, 50), (0, 0, 255), 1, 3, None)
# lb_fps = Label(f"fps: {str(int(fps))}", 100, (WINDOW_WIDTH-175, WINDOW_HEIGHT-50), (175, 50), (255, 255, 255), 1, 3, None)
while not quit:
    # bg[lb_y: , ] = np.ones((WINDOW_HEIGHT-lb_y, WINDOW_WIDTH, 3), dtype="uint8")*111

    cv2.imshow("Push-up Recognition", bg)

    # lb_total.set_text(f"TOTAL: {str(int(count))}")
    # lb_right.set_text(f"RIGHT: {str(no_right)}")
    # lb_wrong.set_text(f"WRONG: {str(no_wrong)}")
    # lb_fps.set_text(f"fps: {str(int(fps))}")

    key = cv2.waitKey(1) & 0xFF
    if eval:
        evaluate(angle_list, filter_list, up_list, down_list)
        eval = False

    if cv2.waitKey(10) == ord("q") or cv2.waitKey(10) == ord("Esc") or quit:
        break

running = False
cv2.destroyAllWindows()

# Create a window and pass it to videoGUI Class
videoGUI(root, "Push-Up App")