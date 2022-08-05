import numpy as np
import cv2
import os, shutil
import PoseModule as pm
import time
import keras
import efficientnet.keras as efn
import matplotlib.pyplot as plt

model_down = keras.models.load_model("models/eff_acc_down.h5")
model_down.summary()