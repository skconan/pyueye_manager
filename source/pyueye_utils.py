#!/usr/bin/env python

from pyueye import ueye
from threading import Thread
import timeit
from utilities import *
import cv2 as cv

"""
    bits_per_pixel
    returns the number of bits per pixel for the given color mode
    raises exception if color mode is not is not in dict
"""
bpp = {
    ueye.IS_CM_SENSOR_RAW8: 8,
    ueye.IS_CM_SENSOR_RAW10: 16,
    ueye.IS_CM_SENSOR_RAW12: 16,
    ueye.IS_CM_SENSOR_RAW16: 16,
    ueye.IS_CM_MONO8: 8,
    ueye.IS_CM_RGB8_PACKED: 24,
    ueye.IS_CM_BGR8_PACKED: 24,
    ueye.IS_CM_RGBA8_PACKED: 32,
    ueye.IS_CM_BGRA8_PACKED: 32,
    ueye.IS_CM_BGR10_PACKED: 32,
    ueye.IS_CM_RGB10_PACKED: 32,
    ueye.IS_CM_BGRA12_UNPACKED: 64,
    ueye.IS_CM_BGR12_UNPACKED: 48,
    ueye.IS_CM_BGRY8_PACKED: 32,
    ueye.IS_CM_BGR565_PACKED: 16,
    ueye.IS_CM_BGR5_PACKED: 16,
    ueye.IS_CM_UYVY_PACKED: 16,
    ueye.IS_CM_UYVY_MONO_PACKED: 16,
    ueye.IS_CM_UYVY_BAYER_PACKED: 16,
    ueye.IS_CM_CBYCRY_PACKED: 16,
}


def get_bits_per_pixel(color_mode):
    print_style("Get bpp", color="blue")
    if bpp.get(color_mode, False):
        print_style("Bits per pixel is", bpp[color_mode], color="yellow")
        return bpp[color_mode]
    else:
        print_style("Bits per pixel is None", color="yellow")
        return None


class uEyeException(Exception):
    def __init__(self, error_code):
        self.error_code = error_code

    def __str__(self):
        return "Err: " + str(self.error_code)


def check(ret):
    if ret != ueye.IS_SUCCESS:
        raise uEyeException(ret)


class ImageBuffer:
    def __init__(self):
        self.mem_ptr = ueye.c_mem_p()
        self.mem_id = ueye.int()


class MemoryInfo:
    def __init__(self, h_cam, img_buff):
        self.x = ueye.int()
        self.y = ueye.int()
        self.bits = ueye.int()
        self.pitch = ueye.int()
        self.img_buff = img_buff

        rect_aoi = ueye.IS_RECT()
        check(ueye.is_AOI(h_cam,
                          ueye.IS_AOI_IMAGE_GET_AOI, rect_aoi, ueye.sizeof(rect_aoi)))
        self.width = rect_aoi.s32Width.value
        self.height = rect_aoi.s32Height.value

        check(ueye.is_InquireImageMem(h_cam,
                                      self.img_buff.mem_ptr,
                                      self.img_buff.mem_id, self.x, self.y, self.bits, self.pitch))


class ImageData:
    def __init__(self, h_cam, img_buff):
        self.h_cam = h_cam
        self.img_buff = img_buff
        self.mem_info = MemoryInfo(h_cam, img_buff)
        self.color_mode = ueye.is_SetColorMode(h_cam, ueye.IS_GET_COLOR_MODE)
        self.bits_per_pixel = get_bits_per_pixel(self.color_mode)
        self.array = ueye.get_data(self.img_buff.mem_ptr,
                                   self.mem_info.width,
                                   self.mem_info.height,
                                   self.mem_info.bits,
                                   self.mem_info.pitch,
                                   True)

    def as_1d_image(self):
        channels = int((7 + self.bits_per_pixel) / 8)
        import numpy
        if channels > 1:
            return numpy.reshape(self.array, (self.mem_info.height, self.mem_info.width, channels))
        else:
            return numpy.reshape(self.array, (self.mem_info.height, self.mem_info.width))

    def unlock(self):
        check(ueye.is_UnlockSeqBuf(
            self.h_cam, self.img_buff.mem_id, self.img_buff.mem_ptr))


class Rect:
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class FrameThread(Thread):
    def __init__(self, cam, device_id, views=None, copy=True):
        super(FrameThread, self).__init__()
        self.timeout = 1000
        self.cam = cam
        self.running = True
        self.views = views
        self.copy = copy
        self.t_old = timeit.default_timer()
        self.device_id = device_id
        cam.set_full_auto()

    def run(self):
        while self.running:

            img_buffer = ImageBuffer()
            ret = ueye.is_WaitForNextImage(self.cam.handle(),
                                           self.timeout,
                                           img_buffer.mem_ptr,
                                           img_buffer.mem_id)
            if ret == ueye.IS_SUCCESS:
                self.notify(ImageData(self.cam.handle(), img_buffer))
                t = timeit.default_timer()
                fps = 1/(t - self.t_old)
                print(fps, ret)
                self.t_old = t

            # break

    def notify(self, image_data):
        img = image_data.as_1d_image()
        image_data.unlock()
        print_style("image shape", img.shape, color="red")
        cv.imshow('Camera ID: '+str(self.device_id), img)
        k = cv.waitKey(1) & 0xff
        if k == ord('q') or k == ord('Q'):
            self.stop()

    def stop(self):
        self.cam.stop_video()
        self.running = False
