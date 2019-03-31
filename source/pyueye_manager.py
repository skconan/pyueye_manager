#!/usr/bin/env python

from pyueye import ueye
from pyueye_camera import Camera
from pyueye_utils import FrameThread

import time
from utilities import *
import cv2
import numpy as np


class Manager:
    def __init__(self):
        self.cam = [0]*10
        self.cam_status = [False]*10

    def get_camera_status(self, n_device_id=5):
        print_style("Camera Status", color="blue")
        for i in range(n_device_id):
            hcam = ueye.HIDS(i)
            ret = ueye.is_InitCamera(hcam, None)

            self.cam_status[i] = not bool(ret)
            if ret == ueye.IS_SUCCESS:
                print_style("Camera ID:", i, " Available", color="green")
            else:
                print_style("Camera ID:", i, " Unavailable", color="red")

    def camera_connect(self, device_id):
        print_style("Camera Connect", mode="blue")
        if self.cam_status[device_id]:
            self.cam[device_id] = Camera(device_id)
            # self.cam[device_id].init()
            self.cam[device_id].alloc()
            
        else:
            print_style("Camera ID:", device_id, " Unavailable", color="red")

    def get_aoi(self):
        rect_aoi = ueye.IS_RECT()
        ueye.is_AOI(self.h_cam, ueye.IS_AOI_IMAGE_GET_AOI,
                    rect_aoi, ueye.sizeof(rect_aoi))

        return Rect(rect_aoi.s32X.value,
                    rect_aoi.s32Y.value,
                    rect_aoi.s32Width.value,
                    rect_aoi.s32Height.value)

if __name__ == "__main__":
    m = Manager()
    m.get_camera_status()
    m.camera_connect(0)
