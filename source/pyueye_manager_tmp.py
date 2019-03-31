#!/usr/bin/env python

from pyueye import ueye
from pyueye_camera import Camera
from pyueye_utils import FrameThread
from utilities import *
import time

import cv2 as cv
import numpy as np


def get_camera_status(n_device_id=5):
    print_style("Camera Status", color="blue")
    for i in range(n_device_id):
        h_cam = ueye.HIDS(i)
        ret = ueye.is_InitCamera(h_cam, None)

        if ret == ueye.IS_SUCCESS:
            print_style("   Camera ID:", i, " Available", color="green")
        else:
            print_style("   Camera ID:", i, " Unavailable", color="red")
        ret = ueye.is_ExitCamera(h_cam)


def main():
    get_camera_status()
    print_style("Insert number of camera(s) that you want to use", color="blue")
    number_of_camera = int(input())
    cam = [[]]*number_of_camera
    thread = [[]]*number_of_camera

    for i in range(number_of_camera):
        print_style("Insert Camera ID", color="blue")
        device_id = int(input())
        cam[i] = Camera()
        cam[i].init()

        cam[i].alloc()
        cam[i].capture_video()

        print_style("Camera ID:", device_id, "Start", color="green")
        thread[i] = FrameThread(cam[i])
        thread[i].start()

    # while True:
        # print_style("Press Q or q to stop camera",color="blue")
        # key = input()
        # if key.islower() == 'q':
        #     break
        # k = cv.waitKey(-1) & 0xff
        # if k == ord('q') or k == ord('Q'):
        #     break

    # for i in range(number_of_camera):
    #     thread[i].stop()
        # thread.join()
        # cam[i].stop_video()
        # cam[i].exit()
        # print_style("Camera ID:", device_id, "Stop", color="red")


if __name__ == "__main__":
    main()
