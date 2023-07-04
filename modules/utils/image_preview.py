import sys
from pathlib import Path
import cv2

from lib.module_base import ModuleBase, ProcessBase


class ImagePreview(ModuleBase):
    last_data = []
    last_image = []

    def process(self, data, image, receiver_channel):

        if 'tracker_data' in self.receiver:
            if receiver_channel == 'image_data':
                self.last_image.append([data, image])
            else:
                self.last_data.append(data)

            break_loop = False
            image_out = None
            for i, (dat, img) in enumerate(self.last_image):
                for j, d in enumerate(self.last_data):
                    if d['timestamp'] == dat['timestamp']:
                        landmarks_x = d['landmark_data'][:68]
                        landmarks_y = d['landmark_data'][68:]
                        for n, (x, y) in enumerate(zip(landmarks_x, landmarks_y)):
                            if d['landmark_visibility'][n] == 1.0:
                                cv2.circle(img, (int(x), int(y)), 3, (127,255,0), -1)
                            else:
                                cv2.circle(img, (int(x), int(y)), 3, (127,0,255), -1)
                        image_out = img
                        self.last_image = self.last_image[i+1:]
                        self.last_data = self.last_data[j+1:]
                        break_loop = True
                        break
                if break_loop:
                    break

            if len(self.last_image) > 2:
                image_out = self.last_image[-3][1]
                self.last_image = self.last_image[-2:]
        else:
            image_out = image

        if image_out is not None:
            cv2.imshow('Image', image_out)
            cv2.waitKey(1)

        return data, image


Module = ProcessBase(ImagePreview)
