import datetime

import cv2
import numpy as np
from tkinter import *
from PIL import Image, ImageTk

# def Photolelo():
#     time = str(datetime.datatime.now().today()).replace(":", " ")+".jpg"
#     img1.save(time)
#
root = Tk()
root.geometry("700x640")
root.configure(bg="black")
Label(root, text="Hello").pack()
f1 = LabelFrame(root, bg="red")
f1.pack()
L1 = Label(f1, bg="red")
L1.pack()
img = cv2.imread("C:\\Users\\Admin\\Pictures\\thanh.jpg")
cap = cv2.VideoCapture(2)
# Button(root, text="Click", command=Photolelo)
while True:
    img = cap.read()[1]
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = ImageTk.PhotoImage(Image.fromarray(img))
    L1['image'] = img
    root.update()

