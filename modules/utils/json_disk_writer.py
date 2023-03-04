import sys
from pathlib import Path
import cv2
from threading import Thread
from lib.module_base import ModuleBase, ProcessBase
import json

class JSONDiskWriter(ModuleBase):

    _data = {}
    _frame = 0
    _fields_to_save = [
        'image_shape',
        'camera',
        'pose',
        'au'
    ]

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

    def process(self, data, image, receiver_channel):
        tmp = {}
        try:
            for k in self._fields_to_save:
                tmp[k] = data[k]

            self._data[self._frame] = tmp
            self._frame += 1
        except TypeError:
            pass
        return data, image

    def finalize(self):
        with open(self.config['json_filename'],'w') as fp:
            json.dump(self._data, fp)

Module = ProcessBase(JSONDiskWriter)
