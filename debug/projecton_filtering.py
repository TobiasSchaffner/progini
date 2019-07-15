import picamera
import picamera.array
import time
import cv2
import numpy as np

# Camera resolution
res_width=1280
res_height=720

# Definition of area of interest
# This is set to the area of the projection
x_off=280
y_off=0
width=680
height=340

# Treshhold for reflections
tresh=15

def init_camera(camera):
    """ Initialize the camera """
    camera.resolution = (res_width, res_height)
    time.sleep(3)

def take_picture(camera):
    """ Take a picture """
    cap=picamera.array.PiRGBArray(camera)
    camera.capture(cap,format="bgr")

    # We are only interested in the projection area
    return cap.array[y_off:y_off+height, x_off:x_off+width]

def main():
    with picamera.PiCamera() as camera:
        init_camera(camera)
        img1 = take_picture(camera)
        while True:
            # Loop delay
            time.sleep(0.5)

            # Take new picture
            img2 = take_picture(camera)

            # Substract to get the difference
            img_neg = cv2.subtract(img1, img2)

            # Filter reflections with treshhold
            ret, filtered_neg = cv2.threshold(img_neg,tresh,255,cv2.THRESH_TOZERO)

            # Get the positive from the negative
            img = cv2.bitwise_not(filtered_neg)

            # Get sum of differing pixels
            img_delta = np.sum(filtered_neg)
            print(img_delta)
    
            # If there is a large difference
            if img_delta > 1000000:
                # There was a big change in the area of interest
                cv2.namedWindow('imageWindow', cv2.WINDOW_AUTOSIZE)
                cv2.imshow('imageWindow',img)
                cv2.waitKey(0)
    
            # The new picture becomes the old picture
            img1 = img2

main()
