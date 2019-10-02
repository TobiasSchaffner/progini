 # Take new picture

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
tresh=30
object_detected = False

def take_picture():
    img_camera = cv2.imread('cam/camera-60.png', cv2.IMREAD_COLOR)
    img_camera = cv2.cvtColor(img_camera, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('camera_0.png', img_camera)
    return img_camera

def orig_screenshot():
    return cv2.imread('screen/screenshot-60.png', cv2.IMREAD_COLOR)

def make_screenshot(height, width):
    screenshot = cv2.imread('screen/screenshot-60.png', cv2.IMREAD_COLOR)
    screenshot = cv2.resize(screenshot, (height, width))
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2GRAY)
    cv2.imwrite('screenshot_0.png', screenshot)
    return screenshot

def removeBackground(camera, screenshot):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    _, camera = cv2.threshold(camera,100,255,cv2.THRESH_BINARY)
    cv2.imwrite('threshold_0.png', camera)
    camera = cv2.erode(camera, kernel, 1)
    cv2.imwrite('errosion_0.png', camera)
    return camera

img_camera = take_picture()
img_old = img_camera

screenshot = make_screenshot(img_camera.shape[1], img_camera.shape[0])

withoutBackground = removeBackground(img_camera, screenshot)

cv2.imwrite('withoutBackground_0.png', withoutBackground)

# Substract to get the difference
img_neg = cv2.subtract(img_old, withoutBackground)
drawable_img = cv2.bitwise_not(img_neg)

# Filter reflections with treshhold
_, filtered_neg = cv2.threshold(img_neg,tresh,255,cv2.THRESH_TOZERO)

cv2.imwrite('filtered_neg_0.png', filtered_neg)

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

# if object_detected:
# Get the biggest contour on the screen
grey_img = filtered_neg# cv2.cvtColor(filtered_neg, cv2.COLOR_BGR2GRAY)
_img, contours, _hierarchy = cv2.findContours(grey_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
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

# Draw a circle at the point of the fingertip
cv2.circle(drawable_img, fingertip, 8, (0, 255, 0), -1)

screenshot_circle = orig_screenshot()

scaled_fingertip = (int(fingertip[0] / width * res_width), int(fingertip[1] / height * res_height))
import pdb; pdb.set_trace()

cv2.circle(screenshot_circle, scaled_fingertip, 8, (0, 255, 0), -1)

cv2.imwrite('out_0.png', drawable_img)
cv2.imwrite('screenshot_circle.png', screenshot_circle)
