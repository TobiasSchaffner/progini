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

object_detected = False

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
    cv2.namedWindow('imageWindow', cv2.WINDOW_AUTOSIZE)
    with picamera.PiCamera() as camera:
        init_camera(camera)
        img_old = take_picture(camera)
        while True:
            # Loop delay
            time.sleep(0.5)

            # Take new picture
            img_new = take_picture(camera)

            # Substract to get the difference
            img_neg = cv2.subtract(img_old, img_new)

            # Filter reflections with treshhold
            _, filtered_neg = cv2.threshold(img_neg,tresh,255,cv2.THRESH_TOZERO)

            # Get the positive from the negative
            img = cv2.bitwise_not(filtered_neg)

            # Get sum of differing pixels
            img_delta = np.sum(filtered_neg)
            print(img_delta)

            # There was a big change in the area of interest
            cv2.imshow('imageWindow',img)
            cv2.waitKey(1)

            # If there is a large difference there is something in the area.
            # In this case keep the old image.
            # if there is nothing in the area use the new image on next iteration.
            if img_delta < 1000000:
                img_old = img_new
                if object_detected:
                    print("Object lost!")
                    object_detected = False
            else:
                if not object_detected:
                    print("Object detected!")
                    object_detected = True

main()
