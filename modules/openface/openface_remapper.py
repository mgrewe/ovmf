import copy
import numpy as np
from scipy.spatial.transform import Rotation

from lib.module_base import ModuleBase, ProcessBase
from lib.auxiliary import get_time_ms


class OpenFaceRemapper(ModuleBase):

    # remap = {
    #     'AU43': 'AU45'
    # }
    
    au_scale = 1.5

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

    def process_control_commands(self, update, receiver_channel = ''):
        pass


    def process(self, data, image, channel_name):

        # Translate
        if ('pose' in data):
            data['pose'][2] *= 2#700

        # Scale AU from [0,5] to [0,1]
        ############### AU's
        if ('au' in data):
            for au in data['au'].keys():
                data['au'][au] = data['au'][au] / 4 * self.au_scale

                if (au == 'AU26'):
                        # Some tuning to keep the mouth closed in rest, an offset seems to be estimated
                        data['au'][au] -= 0.05
                        data['au'][au] = max(0,data['au'][au])
                        #value *= 4/3
                        #val = min(1,val)

                data['au'][au] = min(1,data['au'][au])
            # for au, mapto in self.remap.items:
            #     if (au in data['au']):
            #         data[mapto] = data[au]
            #         data.pop(au)
 

        # Blink
        # blink = parameters['au'][au] / 3
        #     if blink > 1:
        #         blink = 1

        return data, image


Module = ProcessBase(OpenFaceRemapper)
    
