import copy
import numpy as np
from scipy.spatial.transform import Rotation

from lib.module_base import ModuleBase, ProcessBase
from lib.auxiliary import get_time_ms


class OpenFaceRemapper(ModuleBase):

    # Give canonical names to action units
    # In the OVMF, we use the convention AU_{d}, where {d} 
    # is the name (integer) of the AU *without* zero-padding
    remap = {
        # Eye units
        'AU01': 'AU_1',
        'AU02': 'AU_2',
        'AU04': 'AU_4',
        'AU05': 'AU_5',
        'AU06': 'AU_6',
        'AU07': 'AU_7',
        # Nose wrinkler
        'AU09': 'AU_9',
        # Mouth units
        'AU10': 'AU_10',
        'AU12': 'AU_12',
        'AU14': 'AU_14',
        'AU15': 'AU_15',
        'AU17': 'AU_17',
        'AU20': 'AU_20',
        'AU23': 'AU_23',
        'AU25': 'AU_25',
        'AU26' : 'AU_26',
        'AU28' : 'AU_28',
        'AU45' : 'AU_45'
        #'AU28' NA
        }
    
    
    au_scale = 2

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
                data['au'][au] = (data['au'][au] / 4 * self.au_scale) - 0.2

                # if (au == 'AU26'):
                #         # Some tuning to keep the mouth closed in rest, an offset seems to be estimated
                #         data['au'][au] -= 0.1
                #         data['au'][au] = max(0,data['au'][au])
                #         #value *= 4/3
                        #val = min(1,val)

                # Ensure AUs are in [0,1]
                data['au'][au] = max(0,data['au'][au])
                data['au'][au] = min(1,data['au'][au])
            print(data['au'])
            for au, mapto in self.remap.items():
                if (au in data['au']) and not au == mapto:
                    data['au'][mapto] = data['au'][au]
                    data['au'].pop(au)
 
        print(data['au'])
        # Blink
        # blink = parameters['au'][au] / 3
        #     if blink > 1:
        #         blink = 1

        return data, image


Module = ProcessBase(OpenFaceRemapper)
    
