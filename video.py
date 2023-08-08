import cv2 as cv
import cv2
import numpy as np
import matplotlib.pyplot as plt
import asyncio
from loguru import logger
from datetime import datetime
from typing import Tuple


class Instance:
    time: datetime

    def __init__(self) -> None:
        self.time = datetime.now()

    def elapsed(self) -> float:
        return (datetime.now() - self.time).total_seconds()

    def reset(self) -> None:
        self.time = datetime.now()

    def elapsed_reset(self) -> float:
        elapsed = self.elapsed()
        self.reset()
        return elapsed


Mat = cv2.Mat

# preprocess image with color range


def extractByThresh(image: Mat,
                    color_min: Tuple[int, int, int],
                    color_max: Tuple[int, int, int],
                    ) -> Mat:
    blur = cv2.GaussianBlur(image, (5, 5), 2, 2)
    lab = cv2.cvtColor(blur, cv2.COLOR_BGR2LAB)
    l_min, a_min, b_min = color_min
    l_max, a_max, b_max = color_max
    lab_red = cv2.inRange(lab, np.array(
        [l_min, a_min, b_min]), np.array([l_max, a_max, b_max]))
    lab_red = cv2.erode(lab_red, (3, 3), iterations=3)
    lab_red = cv2.dilate(lab_red, (3, 3), iterations=3)

    blur_again = cv2.GaussianBlur(lab_red, (5, 5), 2, 2)
    return blur_again


def handle_frame(frame: cv2.Mat) -> cv2.Mat:
    color_min_red = (10, 144, 121)
    color_max_red = (245, 255, 152)
    color_min_green = (18, 60, 135)
    color_max_green = (245, 108, 255)
    crop_frame = frame[0:550, 170:740]
    binary = extractByThresh(crop_frame, color_min_red,
                             color_max_red)  # type: ignore
    # https://docs.opencv.org/3.4/d0/d7a/classcv_1_1SimpleBlobDetector.html
    params = cv2.SimpleBlobDetector_Params()
    from math import pi
    # https://www.geeksforgeeks.org/find-circles-and-ellipses-in-an-image-using-opencv-python/
    params.filterByCircularity = False
    params.filterByConvexity = False
    params.filterByInertia = False
    params.filterByColor = False
    params.filterByArea = True
    params.minArea = pi * 1 ** 2
    params.maxArea = pi * 10 ** 2
    blob = cv2.SimpleBlobDetector_create(params)
    # blob.filterByArea = True
    # https://stackoverflow.com/questions/20466676/simpleblobdetector-filtering-by-area
    kps = blob.detect(binary)
    for kp in kps:
        x, y = kp.pt
        cv2.circle(crop_frame, (int(x), int(y)), 10, (0, 0, 255), -1)
        logger.info(f"Found blob at {x}, {y}")

    ret = crop_frame
    return ret  # type: ignore


async def runVideo():
    frame_instance = Instance()
    fps = 30
    duration_ms = (1 / fps) * 1000
    cap = cv2.VideoCapture("test.avi")
    while True:
        ret, frame = cap.read()
        if ret:
            r = handle_frame(frame)
            cv.imshow("frame", r)
            if cv.waitKey(1) & 0xFF == ord('q'):
                exit()
            elapsed = frame_instance.elapsed()
            diff = duration_ms - elapsed
            if diff < 0:
                logger.warning(
                    f"Frame took {elapsed}ms, which is longer than {duration_ms}ms")
            await asyncio.sleep(diff / 1000)
            frame_instance.reset()
        else:
            logger.warning("No frame")
            exit()


def main():
    loop = asyncio.get_event_loop()
    # https://superfastpython.com/asyncio-run_coroutine_threadsafe/
    asyncio.run_coroutine_threadsafe(runVideo(), loop)
    loop.run_forever()
    loop.close()

# https://docs.opencv.org/3.4/d0/d7a/classcv_1_1SimpleBlobDetector.html
# https://learnopencv.com/blob-detection-using-opencv-python-c/
# https://docs.arduino.cc/tutorials/nicla-vision/blob-detection


if __name__ == "__main__":
    main()
