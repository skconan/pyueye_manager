#!/usr/bin/env python

from pyueye import ueye
from pyueye_camera import Camera
from pyueye_utils import FrameThread

import time

import cv2
import numpy as np

def main():
    cam = Camera()
    cam.init()

    cam.alloc()
    cam.capture_video()

    thread = FrameThread(cam)
    thread.start()

    time.sleep(1) 

    thread.stop()
    # thread.join()

    cam.stop_video()
    cam.exit()

if __name__ == "__main__":
    main()