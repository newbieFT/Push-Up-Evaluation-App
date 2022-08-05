from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import PIL.Image, PIL.ImageTk
from PIL import Image, ImageTk
import cv2

#Set the interface:
root = Tk()
root.title("Push-Up App")
root.geometry("1200x720")
root.iconbitmap("icon_image/LOGO.ico")


# Set background for app
input_file = Image.open("icon_image/background.png")
bgr = ImageTk.PhotoImage(input_file)
img = Label(root, image=bgr)
img.place(x=0, y=0)

#Title
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

VIDEO_WIDTH = 576
VIDEO_HEIGHT = 320
def btn_file_action():
    pass

class videoGUI:
    
    def __init__(self, window, window_title):

        self.window = window
        self.window.title(window_title)
        

        top_frame = Frame(self.window)
        top_frame.place(x=110, y=150)

        bottom_frame = Frame(self.window)
        bottom_frame.place(x=270, y=500)

        self.pause = False   # Parameter that controls pause button

        self.canvas = Canvas(top_frame, bg="white", height=VIDEO_HEIGHT, width=VIDEO_WIDTH)
        self.canvas.pack()

        # Play Button
        self.btn_play = Button(bottom_frame, text="Play  ---", fg="#FFFFFF", bg="#010D1D", borderwidth=5, command=self.play_video)
        self.btn_play.config(font=("Transformers Movie", 10))
        self.play_icon_button = Button(button_frame, image=icon_play, font=("Arial", 30, "bold"), fg="#FFFFFF",
                                       bg="#001E3D", borderwidth=3, command=self.play_video)
        self.play_icon_button.place(x=309, y=504)
        self.btn_play.grid(row=0, column=1)

        # Pause Button
        self.btn_pause = Button(bottom_frame, text="Pause    ", fg="#FFFFFF", bg="#010D1D", borderwidth=5, command=self.pause_video)
        self.btn_pause.config(font=("Transformers Movie", 10))
        self.pause_icon_button = Button(button_frame, image=icon_pause, font=("Arial", 30, "bold"), fg="#FFFFFF",
                                       bg="#001E3D", borderwidth=3, command=self.pause_video)
        self.pause_icon_button.place(x=390, y=504)
        self.btn_pause.grid(row=0, column=2)

        # Resume Button
        self.btn_resume = Button(bottom_frame, text="Resume    ", fg="#FFFFFF", bg="#010D1D", borderwidth=5, command=self.resume_video)
        self.btn_resume.config(font=("Transformers Movie", 10))
        self.resume_icon_button = Button(button_frame, image=icon_play, font=("Arial", 30, "bold"), fg="#FFFFFF",
                                       bg="#001E3D", borderwidth=3, command=self.resume_video)
        self.resume_icon_button.place(x=481, y=504)
        self.btn_resume.grid(row=0, column=3)

        # Open File Button
        self.file_button = Button(button_frame, text="Open File ---", fg="#FFFFFF", bg="#010D1D", borderwidth=10, command=self.open_file)
        self.file_button.config(font=("Transformers Movie", 30))
        self.file_icon_button = Button(button_frame, image=icon_file, font=("Arial", 30, "bold"), fg="#FFFFFF",
                                       bg="#001E3D", borderwidth=3, command=self.open_file)
        self.file_icon_button.place(x=1105, y=210)
        self.file_button.place(x=900, y=180)

        # Camera Button
        self.camera_button = Button(button_frame, text="Camera ---", fg="#FFFFFF", bg="#010D1D", borderwidth=10, command=btn_file_action)
        self.camera_button.config(font=("Transformers Movie", 30))
        self.camera_icon_button = Button(button_frame, image=icon_camera, font=("Arial", 30, "bold"), fg="#FFFFFF",
                                         bg="#001E3D", borderwidth=3, command=btn_file_action)
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
        self.total_icon_button = Button(button_frame, image=icon_total, font=("Arial", 30, "bold"), fg="#FFFFFF", bg="#001E3D", borderwidth=3)
        self.total_icon_button.place(x=655, y=623)
        self.total_button.place(x=645, y=610)

        # Stop Button
        self.stop_button = Button(button_frame, text="Stop --", fg="#FFFFFF", bg="#010D1D",
                             borderwidth=10, command=btn_file_action)
        self.stop_button.config(font=("Transformers Movie", 30))
        self.stop_icon_button = Button(button_frame, image=icon_stop, font=("Arial", 30, "bold"), fg="#FFFFFF", bg="#001E3D", borderwidth=3)
        self.stop_icon_button.place(x=1010, y=527)
        self.stop_button.place(x=900, y=500)
        
        self.delay = 15   # ms

        self.window.mainloop()


    def open_file(self):

        self.pause = False

        self.filename = filedialog.askopenfilename(title="Select file", filetypes=(("MP4 files", "*.mp4"),
                                                                                         ("WMV files", "*.wmv"), ("AVI files", "*.avi")))
        print(self.filename)

        # Open the video file
        self.cap = cv2.VideoCapture(self.filename)

        self.width = VIDEO_WIDTH
        self.height = VIDEO_HEIGHT

        self.canvas.config(width=self.width, height=self.height)


    def get_frame(self):   # get only one frame

        try:

            if self.cap.isOpened():
                ret, frame = self.cap.read()
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        except:
            messagebox.showerror(title='Video file not found', message='Please select a video file.')


    def play_video(self):

        # Get a frame from the video source, and go to the next frame automatically
        ret, org_frame = self.get_frame()
        frame = cv2.resize(org_frame, dsize=(VIDEO_WIDTH, VIDEO_HEIGHT))
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=NW)

        if not self.pause:
            self.window.after(self.delay, self.play_video)


    def pause_video(self):
        self.pause = True

#Addition
    def resume_video(self):
        self.pause = False
        self.play_video()


    # Release the video source when the object is destroyed
    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()

##### End Class #####


# Create a window and pass it to videoGUI Class
videoGUI(root, "Push-Up App")