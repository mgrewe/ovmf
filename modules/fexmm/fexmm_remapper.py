import copy
import numpy as np
from scipy.spatial.transform import Rotation

from lib.module_base import ModuleBase, ProcessBase
from lib.auxiliary import get_time_ms


class FexMMRemapper(ModuleBase):
    
    # Determine which movements should be transfered
    send_aus = True
    send_location = True
    send_rotation = True
    send_eyes = True
    
    # OpenFace AU, (FexMM Shapekey, scaling factor)
    catch_au = {
            # Eye units
            'AU_1': ('AU_1', 1),
            'AU_2': ('AU_2', 1),
            'AU_4': ('AU_4', 1),
            'AU_5': ('AU_5', 1),
            'AU_6': ('AU_6', 1),
            'AU_7': ('AU_7', 1),
            # Nose wrinkler
            'AU_9': ('AU_9', 1),
            # Mouth units
            'AU_10': ('AU_10', 1),
            'AU_12': ('AU_12', 1),
            'AU_14': ('AU_14', 1),
            'AU_15': ('AU_15', 1),
            'AU_17': ('AU_17', 1),
            'AU_20': ('AU_20', 1),
            'AU_23': ('AU_18', 1),
            'AU_25': ('AU_25', 1),
            'AU_26' : ('AU_26', 1)
            #'AU28' NA
            }
    
    # We do not have specific blink AUs, so remap to AU43
    blink = {'AU45': ['AU_43'] }
    
    
    parameter_history = None

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

        if 'maps' in config:
            if ('l' not in config['maps']):
                print('Not sending location')
                self.send_location = False
            if ('r' not in config['maps']):
                print('Not sending rotation')
                self.send_rotation = False
            if ('a' not in config['maps']):
                print('Not sending aus')
                self.send_aus = False
            if ('e' not in config['maps']):
                print('Not sending eyes')
                self.send_eyes = False

    def process_control_commands(self, update, receiver_channel = ''):
        pass


    def process(self, data, image, channel_name):
        fexmm_parameters = copy.deepcopy(data)


        ############### AU's
        if (self.send_aus and 'au' in data):

            fexmm_parameters['au'] = {}
            for au, (fexmm, fac) in self.catch_au.items():
                if au in data['au']:
                    fexmm_parameters['au'][fexmm] = data['au'][au] * fac
            fexmm_parameters['au'][fexmm]
        
        ################ EYES
        
        if (self.send_eyes):
            if ('au' in data):
                for au, fexmm in self.blink.items():
                    if au in data['au']:
                        for f in fexmm:
                            fexmm_parameters['au'][f] = data['au'][au]
             
            if ('gaze' in data):
                gaze = np.array(data['gaze'])
                # need to compensate for head pose in gaze estimation
                gaze = np.array([gaze[1], 0, -gaze[0]])
                rot_gaze = Rotation.from_euler('XYZ', gaze)
 
                if (self.send_rotation and 'pose' in data):
                    rotation = np.array(data['pose'][3:6])
                    head_rotation = Rotation.from_euler('XYZ', rotation)
                    rot_gaze = head_rotation.inv() * rot_gaze   
                 
                fexmm_parameters['eye_gaze'] = rot_gaze.as_euler('XYZ').tolist()
        
        return fexmm_parameters, image


Module = ProcessBase(FexMMRemapper)
    
