'''
Copyright (C) 2014 Hernaldo Jesus Henriquez Nunez

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
'''

import cv2 as cv
import numpy as np


ESC_KEY = 27
current_img = 0
segmentation_img = 0
# If option_rgb is true the range will be BGR, else it will be HSV
option_rgb = True
img_count = 0
is_rgb = True


def nothing(x):
    pass


def refresh():
    global current_img
    global segmentation_img
    global is_rgb
    global option_rgb

    ch1_min = cv.getTrackbarPos("min_channel1", "Bars")
    ch1_max = cv.getTrackbarPos("max_channel1", "Bars")
    ch2_min = cv.getTrackbarPos("min_channel2", "Bars")
    ch2_max = cv.getTrackbarPos("max_channel2", "Bars")
    ch3_min = cv.getTrackbarPos("min_channel3", "Bars")
    ch3_max = cv.getTrackbarPos("max_channel3", "Bars")

    min_range = np.array([ch1_min, ch2_min, ch3_min])
    max_range = np.array([ch1_max, ch2_max, ch3_max])

    current_img = cv.cvtColor(current_img, cv.COLOR_BGR2LAB)

    segmentation_img = cv.inRange(current_img, min_range, max_range)
    cv.imshow("Segmentation", segmentation_img)


def main():
    '''
	runs a window with the camera image, a processed image and the trackbars for
	the inRange
	'''
    global current_img
    global segmentation_img
    global img_count
    global is_rgb

    opt = 0

    ################################################################################
    #####################            Using Video               #####################
    ################################################################################

    if opt == 0:
        video = cv.VideoCapture(1)
        IMG_W = 960
        IMG_H = 720
        video.set(cv.CAP_PROP_FRAME_WIDTH, IMG_W)
        video.set(cv.CAP_PROP_FRAME_HEIGHT, IMG_H)
        video.set(cv.CAP_PROP_BRIGHTNESS, 20)
        video.set(cv.CAP_PROP_CONTRAST,45)
        video.set(cv.CAP_PROP_SATURATION,68)
        video.set(cv.CAP_PROP_GAMMA,400)
        # video.set(cv.CAP_PROP_FOURCC, cv.VideoWriter.fourcc('Y', 'U', 'Y', 'V'))
        video.set(cv.CAP_PROP_FOURCC, cv.VideoWriter.fourcc('M', 'J', 'P', 'G'))
        # Important windows
        cv.namedWindow("Bars")
        # cv.namedWindow("Segmentation")
        # cv.namedWindow("Video")
        cv.createTrackbar("min_channel1", "Bars", 0, 254, nothing)
        cv.createTrackbar("max_channel1", "Bars", 255, 255, nothing)
        cv.createTrackbar("min_channel2", "Bars", 0, 254, nothing)
        cv.createTrackbar("max_channel2", "Bars", 255, 255, nothing)
        cv.createTrackbar("min_channel3", "Bars", 0, 254, nothing)
        cv.createTrackbar("max_channel3", "Bars", 255, 255, nothing)
        pause = False
        while True:
            if not pause:
                ret, current_img = video.read()
                current_img = current_img[140:-150, 420:-250]
                if not ret:
                    break
                cv.imshow("Video", current_img)
            is_rgb = True
            refresh()
            key = cv.waitKey(33)
            if key == ord(' '):
                pause = not pause
                print ("Video paused")
            elif key == ord('q'):
                break

            elif key == ord('s'):
                filename = "{0}.jpg".format(img_count)
                cv.imwrite(filename, current_img)
                print ("Image saved as {0}".format(filename))
                img_count = img_count + 1
            elif key == 27:
                break
        video.release()

    ################################################################################
    #####################            Using Image               #####################
    ################################################################################

    
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()
