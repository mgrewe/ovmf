from threading import Thread, Lock, Event
from copy import copy
import numpy as np
import bpy, gpu
from lib.module_base import ModuleBase
from lib.auxiliary import get_time_ms

# Color conversion from blender internal to sRGB
# https://blender.stackexchange.com/questions/107048/blender-linear-rgb-to-srgb-conversion
# def RGB2sRGB2(RGBArray):
#     new_rgb = RGBArray
#     higher = (new_rgb > 0.0031308)
#     lower = (new_rgb <= 0.0031308)
#     new_rgb[higher] = (pow(new_rgb[higher], (1.0 / 2.4))) * 1.055 - 0.055
#     new_rgb[lower] = 12.92 * new_rgb[lower]
#     return new_rgb

#adapted to numpy
def linear_to_srgb(linear):
    srgb = linear
    higher = linear > 0.0031308
    lower  = linear < 0.0031308
    srgb[higher] = (linear[higher]**(1.0/2.4)) * 1.05 - 0.05
    srgb[lower] = 12.92 * linear[lower]
    return srgb

class BlenderRenderOutput(ModuleBase):
    buffer = None
    running = False
    image = None
    image_buffer = None
    lock = Lock()
    data = None
    new_image = Event()


    def __init__(self, config, start_sender_thread = False, **kwargs):
        self.start_sender_thread = start_sender_thread
        super().__init__(config, **kwargs)

    def process(self, data, image, receiver_channel = ''):
        data, image = self.take_snapshot(data, False)
        if not self.start_sender_thread:
            self.send_image()
        return data,image

    def process_and_measure(self, data, image, receiver_channel = ''):
        data, image = self.take_snapshot(data, True)
        if not self.start_sender_thread:
            self.send_image()
        return data,image

    def start_streaming(self):
        print("Start streaming...")

        if self.start_sender_thread:
            print("Using async sender thread.")
            self.sender_thread = Thread(target = self.run, args=(self,))
            self.running = True
            self.sender_thread.start()  

    def stop_streaming(self):
        print("Stop streaming...", flush=True)
        if self.start_sender_thread:
            self.running = False
            self.sender_thread.join()
        
    @staticmethod
    def run(self):
        while (self.running):
            self.send_image()

    def send_image(self):
        if self.running and not self.new_image.wait(timeout = 0.1):
            return
        self.lock.acquire()
        if self.image is not None:
            self.sender.send(msg = self.data, img = self.image)
            self.new_image.clear()
        self.lock.release()
    
    def take_snapshot(self, data, measure_time = True):

        start = get_time_ms()

        self.lock.acquire()
        

        framebuffer = gpu.state.active_framebuffer_get()
        viewport_info = gpu.state.viewport_get()
        width = viewport_info[2]
        height = viewport_info[3]


        if (self.image_buffer is None or self.image.shape[0:2] != (height, width)):
            self.image_buffer = np.zeros([height, width, 4],dtype=np.float32)
            self.buffer = gpu.types.Buffer('FLOAT', self.image_buffer.shape, self.image_buffer)

        pixelBuffer = framebuffer.read_color(0, 0, width, height, 4, 0, 'FLOAT', data=self.buffer)


        self.image = (linear_to_srgb(self.image_buffer)*255.).astype('uint8')

        # import cv2
        # cv2.imshow("Test", cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))
        # cv2.waitKey(1)

        end = get_time_ms()

        self.data = copy(data)
        self.new_image.set()
        self.lock.release()

        return data, self.image
