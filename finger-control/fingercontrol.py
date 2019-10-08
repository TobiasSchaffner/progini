import cv2
import datetime
import mss
import numpy as np
import os
import pyautogui
import sys
import time
from camera import CameraFactory

# enable debug output
debug = False
DEBUG_SWITCHES = ['-v', 'debug', '--verbose', 'DEBUG']

# Screen resolution
SCREEN_WIDTH=1280
SCREEN_HEIGHT=720

# Definition of area of interest
# This is set to the area of the projection
X_OFFSET=280
Y_OFFSET=0
WIDTH=680
HEIGHT=340

# Thresholds
REFLECTIONS_THRESHOLD=30
MOVEMENT_THRESH=100000

# Image processing iteration (for debugging only)
iteration = 0


def to_grayscale(image):
    result = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return result


def clip_projection_area(image):
    result = image[Y_OFFSET : (Y_OFFSET + HEIGHT), X_OFFSET : (X_OFFSET + WIDTH)]
    return result


def preprocess_image(image):
    clipped = clip_projection_area(image)
    grayscale = to_grayscale(clipped)

    if debug: output_debug_image('grayscale_photo', grayscale)

    return grayscale


def remove_background(camera):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    _, backgroundRemoved = cv2.threshold(camera, 100, 255, cv2.THRESH_BINARY)

    if debug: output_debug_image('background_removed', backgroundRemoved)

    eroded = cv2.erode(camera, kernel, 1)

    if debug: output_debug_image('background_removed_eroded', eroded)

    return eroded


def calc_threshold_image(old_image, new_image):
    img_neg = cv2.subtract(old_image, new_image)
    drawable_img = cv2.bitwise_not(img_neg)

    # Filter reflections with treshhold
    _, filtered_neg = cv2.threshold(img_neg, REFLECTIONS_THRESHOLD, 255, cv2.THRESH_TOZERO)

    if debug: output_debug_image('filtered_neg', filtered_neg)

    return filtered_neg


def detectMovement(pixel_delta):
    # If there is a large difference there is something in the area.
    # In this case keep the old image.
    # if there is nothing in the area use the new image on next iteration.
    if pixel_delta < MOVEMENT_THRESH:
        print("Movement stoped!")
        return False
    else:
        print("Movement detected!")
        return True


def determine_contour_maximum_point(image):
    # Get the biggest contour on the screen
    _img, contours, _hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    biggest_contour = max(contours, key = cv2.contourArea)

    # Get the extrem points of the biggest contour.
    left = tuple(biggest_contour[biggest_contour[:, :, 0].argmin()][0])
    right = tuple(biggest_contour[biggest_contour[:, :, 0].argmax()][0])
    top = tuple(biggest_contour[biggest_contour[:, :, 1].argmin()][0])
    bot = tuple(biggest_contour[biggest_contour[:, :, 1].argmax()][0])

    # Assume that the fingertip is on the opposite of the side the hand enters the area of interest.
    fingertip = None
    if (bot[1] == HEIGHT - 1):
        return top
    elif (left[0] == 0):
        return right
    elif (right[0] == WIDTH - 1):
        return left
    elif (top[1] == 0):
        return bot


def scale_position_to_screen(cam_position):
    x = cam_position[0] / WIDTH * SCREEN_WIDTH
    y = cam_position[1] / HEIGHT * SCREEN_HEIGHT

    return (int(x), int(y))


def move_mouse_to(position):
    pyautogui.moveTo(position[0], position[1])


def click_at(position):
    pyautogui.click(position[0], position[1])


def started_in_debug_mode():
    for argument in sys.argv:
        if argument in DEBUG_SWITCHES:
            return True
    return False


def create_debug_folder():
    timeString = time.strftime("%Y-%m-%d-%H-%M-%S")
    folderDebugImages = 'debug_images_{}'.format(timeString)
    os.mkdir(folderDebugImages)
    return folderDebugImages


def output_debug_image(name, image):
    global iteration
    cv2.imwrite('{}/{}-{}.png'.format(folderDebugImages, name, iteration), image)


def main():
    global iteration

    # TODO implement dry run switch
    camera = CameraFactory.create('camera')
    with camera:
        camera.initialize()
        img_old = preprocess_image(camera.take_picture(iteration))
        while True:
            original = camera.take_picture(iteration)

            if debug: output_debug_image('original', original)

            img_new = remove_background(preprocess_image(original))

            threshold_img = calc_threshold_image(img_old, img_new)
            img_delta = np.sum(threshold_img)
            print(img_delta)

            if detectMovement(img_delta):
                fingertip = determine_contour_maximum_point(threshold_img)

                if fingertip is not None:
                    # Draw a circle at the point of the fingertip
                    cv2.circle(threshold_img, fingertip, 8, (255, 0, 0), -1)

                    if debug: output_debug_image('threshold_img', threshold_img)

                    click_at(scale_position_to_screen(fingertip))

            img_old = img_new
            iteration = iteration + 1

folderDebugImages = 'debug_images'
debug = started_in_debug_mode()
if debug:
    folderDebugImages = create_debug_folder()

main()
