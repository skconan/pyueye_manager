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
        self.cam_status = [0]*10
        self.get_camera_status()

    def get_camera_status(self, n_device_id=5):
        print_style("Camera Status", color="blue")
        for i in range(n_device_id):
            self.cam[i] = ueye.HIDS(i)
            ret = ueye.is_InitCamera(cam, None)
            self.cam_status[i] = not bool(ret)
            if ret == ueye.IS_SUCCESS:
                print_style("Camera ID:", i, " Available", color="green")
            else:
                print_style("Camera ID:", i, " Unavailable", color="red")

    # def camera_connection(self, device_id):
    #     if self.cam_status[device_id]:


# if __name__ == "__main__":
