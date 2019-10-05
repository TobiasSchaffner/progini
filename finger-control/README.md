# Progini - Finger Control

This python script takes the input from the lantern camera and moves the mouse cursor to the tip of your finger.
Most of the time...

## Requirements

* `python3 python3-pip python3-tk python3-dev python3-opencv scrot` installed
* PiP Packages declared in requirements.txt (`pip install -r requirements.txt`)

# Run it

Move or clone the folder on your lantern / raspberry pi and execute the script with `python3 fingercontrol.py`.
The mouse will try to follow your finger tip now.

After starting the script the device is ready when you see numbers running down the terminal.
These numbers are an indicator on how much changed in the current picture.

# Whats going on

Its starting with an image we get from the pi camera.
This image is fully colored, but since we only need some positions we convert it to greyscale and also cut out the area of interest.
The area of interest is defined as the part of the image where the projection is located.

After greyscale we set an threshold on the image to distinguish between the not-interesting part (table and reflections) and the interesting-part (your finger).
We assume that the finger is always darker then the projection surface and filter out the lit up parts of the image.
To fill gaps in close contours we apply a erosion with a 5x5 filter on it.

To determine if we have a movement in the image we simply count the different pixels from the cam image before the current one.
If the difference count is over a threshold we assume movement.

On movement OpenCV is detecting all contours in the thresholded image and we pick the biggest one.
Here we think that the biggest one must be the finger connected to your hand.
We also assume that the extrema on the opposite direction of the place your hand enters the image, is your fingertip.

So in the last step we move the mouse pointer to the resolution-scaled coordinates of the detected fingertip.
