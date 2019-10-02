import picamera
import picamera.array
import time
import cv2
import numpy as np
import mss
import pyautogui

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
tresh=30

def init_camera(camera):
    """ Initialize the camera """
    camera.resolution = (res_width, res_height)
    time.sleep(3)

def take_picture(camera):
    """ Take a picture """
    cap=picamera.array.PiRGBArray(camera)
    camera.capture(cap,format="bgr")

    # We are only interested in the projection area
    result = cap.array[y_off:y_off+height, x_off:x_off+width]
    return cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

def removeBackground(camera):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    _, camera = cv2.threshold(camera,100,255,cv2.THRESH_BINARY)
    camera = cv2.erode(camera, kernel, 1)
    return camera

def main():
    object_detected = False
    cv2.namedWindow('imageWindow', cv2.WINDOW_AUTOSIZE)
    with picamera.PiCamera() as camera:
        init_camera(camera)
        img_old = take_picture(camera)
        index = 0
        while True:

            img_new = removeBackground(take_picture(camera))
            # Substract to get the difference
            img_neg = cv2.subtract(img_old, img_new)
            drawable_img = cv2.bitwise_not(img_neg)

            # Filter reflections with treshhold
            _, filtered_neg = cv2.threshold(img_neg,tresh,255,cv2.THRESH_TOZERO)

            # Get sum of differing pixels
            img_delta = np.sum(filtered_neg)
            print(img_delta)

            # If there is a large difference there is something in the area.
            # In this case keep the old image.
            # if there is nothing in the area use the new image on next iteration.
            if img_delta < 300000:
                if object_detected:
                    print("Object lost!")
                    object_detected = False
            else:
                if not object_detected:
                    print("Object detected!")
                    object_detected = True

            if object_detected:
                # Get the biggest contour on the screen
                _img, contours, _hierarchy = cv2.findContours(filtered_neg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                biggest_contour = max(contours, key = cv2.contourArea)

                # Get the extrem points of the biggest contour.
                left = tuple(biggest_contour[biggest_contour[:, :, 0].argmin()][0])
                right = tuple(biggest_contour[biggest_contour[:, :, 0].argmax()][0])
                top = tuple(biggest_contour[biggest_contour[:, :, 1].argmin()][0])
                bot = tuple(biggest_contour[biggest_contour[:, :, 1].argmax()][0])

                # Assume that the fingertip is on the opposite of the side the hand enters the area of interest.
                fingertip = None
                if (bot[1] == height - 1):
                    fingertip = top
                elif (left[0] == 0):
                    fingertip = right
                elif (right[0] == width - 1):
                    fingertip = left
                elif (top[1] == 0):
                    fingertip = bot

                if fingertip is not None:
                    # Draw a circle at the point of the fingertip
                    cv2.circle(drawable_img, fingertip, 8, (0, 255, 0), -1)
                    scaled_fingertip = (int(fingertip[0] / width * 1280), int(fingertip[1] / height * 720))

                    pyautogui.moveTo(scaled_fingertip[0], scaled_fingertip[1])
            else:
                img_old = img_new

            # cv2.imshow('imageWindow', drawable_img)
            # cv2.waitKey(1)

main()
