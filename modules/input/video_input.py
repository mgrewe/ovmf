import sys
from lib.module_base import ModuleBase, ProcessBase
import numpy as np
import cv2
from modules.input.webcam_input import WebcamInput
from lib.auxiliary import get_time_ms

class VideoInput(ModuleBase):

    current_frame = 0
    delay = 0.0
    images = None
    last_frame = None
    intrinsics = None

    def __init__(self, config,  **kwargs):

        super().__init__(config, **kwargs)

        if not 'video_filename' in config or config['video_filename'] == "":
            raise ValueError("VideoInput requires filename in config")

        print("Reading video from ", config['video_filename'])

        scale = float(config['scale']) if 'scale' in config else 1.0

        self.images = []
        vid = cv2.VideoCapture(config['video_filename'])
        width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH) * scale)
        height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT) * scale)
        self.intrinsics = WebcamInput.guessIntrinsics(width, height)
        fps = int(vid.get(cv2.CAP_PROP_FPS))
        print('Video opened with resolution {0:d}x{1:d} and {2:d} fps.'.format(width, height, fps))
        hflip = False
        if ('video_input_hflip' in config and config['video_input_hflip']):
            print("Flipping video input horizontally.")
            hflip = True
        vflip = False
        if ('video_input_vflip' in config and config['video_input_vflip']):
            print("Flipping video input vertically.")
            vflip = True

        while True:
            ret, image = vid.read()
            if not ret:
                break
            image = cv2.resize(image,(0,0), fx = scale, fy = scale)
            image = cv2.resize(image,(0,0), fx = scale, fy = scale)
            if hflip:
                image = cv2.flip(image, 1)
            if vflip:
                image = cv2.flip(image, 0)
            self.images.append(image)
        print('Read ' + str(len(self.images)) + " frames.")

        if 'fps' in config:
            self.delay = 1.0 / float(config['fps'])

    def get_num_frames(self):
        return len(self.images)
    
    def process(self, data, image, receiver_channel):


        current_time = get_time_ms() / 1000

        if (not self.last_frame == None) and current_time < (self.last_frame + self.delay):
            return data, image
                   

        # true_frame = self.current_frame self.current_frame

        image = self.images[self.current_frame]
        data = {}
        data['timestamp'] = current_time
        data['image_shape'] = image.shape
        data['camera'] = self.intrinsics

        self.last_frame  = current_time
        self.current_frame = (self.current_frame + 1) % self.get_num_frames()

        # print(self.delay, self.current_frame)
        return data, image



Module = ProcessBase(VideoInput)

