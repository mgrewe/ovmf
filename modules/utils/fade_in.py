import numpy as np
from lib.module_base import ModuleBase, ProcessBase


class FadeIn(ModuleBase):
    fade = 0;
    fade_in_duration = 0;
    fade_in_pose = False;

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        if ('fade_in_duration' in config):
            self.fade_in_duration = float(config['fade_in_duration'])
        if ('fade_in_pose' in config):
            self.fade_in_duration = float(config['fade_in_pose'])

    def process(self, data, image, receiver_channel):
        if 'pose' in data.keys():
            if self.fade_in_pose:
                data['pose'] = (np.array(data['pose']) * self.fade).tolist()

        if 'au' in data.keys():
            for key, value in data['au'].items():
                data['au'][key] = value * self.fade
        self.fade += 1/self.fade_in_duration
        self.fade = min(self.fade,1)
        return data, image


Module = ProcessBase(FadeIn)
