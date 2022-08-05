from PIL import Image
import os, sys

path = "C:/Users/Admin/Documents/AI Project/Data Set/Up Right/"
dirs = os.listdir( path )

def resize():
    for item in dirs:
        if os.path.isfile(path+item):
            im = Image.open(path+item)
            f, e = os.path.splitext(path+item)
            imResize = im.resize((224,224), Image.ANTIALIAS)
            imResize.save(fp=item+".jpg")

resize()

#Delete Image
# import glob
# removing_files = glob.glob('C:/Users/Admin/Documents/AI Project/Data Set/Down Right/*resized.jpg')
# for i in removing_files:
#     os.remove(i)