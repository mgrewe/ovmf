import sys
import pathlib as pl
import copy
import numpy as np
from scipy.spatial.transform import Rotation

dir = str(pl.Path(__file__).resolve().parents[2])
if not dir in sys.path:
    sys.path.append(dir)
from lib.module_base import ModuleBase, ProcessBase
from lib.auxiliary import get_time_ms


class OpenFaceToFexMMRemapper(ModuleBase):
    
    # Determine which movements should be transfered
    send_aus = True
    send_location = True
    send_rotation = True
    send_eyes = True
    
    # OpenFace AU, (FexMM Shapekey, scaling factor)
    catch_au = {
            # Eye units
            'AU01': ('AU_1', 1),
            'AU02': ('AU_2', 1),
            'AU04': ('AU_4', 1),
            'AU05': ('AU_5', 1),
            'AU06': ('AU_6', 1),
            'AU07': ('AU_7', 1),
            # Nose wrinkler
            'AU09': ('AU_9', 1),
            # Mouth units
            'AU10': ('AU_10', 0.2),
            'AU12': ('AU_12', 1),
            'AU14': ('AU_14', 1),
            'AU15': ('AU_15', 1),
            'AU17': ('AU_17', 1),
            'AU20': ('AU_20', 1),
            'AU23': ('AU_23', 1),
            'AU25': ('AU_25', 1),
            'AU26' : ('AU_26', 2)
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
        parameters = data
        fexmm_parameters = copy.deepcopy(parameters)

        ############## LOCATION
        
        if (self.send_location and 'pose' in parameters):
            location = np.array(parameters['pose'][0:3])
            # Scale to blender units
            location[2] -= 700
            location *= 0.01
            
            fexmm_parameters['location'] = [-location[0], location[2], -location[1]]

        ############## ROTATION

        if (self.send_rotation and 'pose' in parameters):        
            rotation = np.array(parameters['pose'][3:6])
            rotation = np.array([rotation[0], -rotation[2], rotation[1]])
            fexmm_parameters['rotation'] = rotation.tolist()

        ############### AU's
        if (self.send_aus and 'au' in parameters):
            fexmm_parameters['shapekeys'] = {}
            for openface, (fexmm, fac) in self.catch_au.items():
                if openface in parameters['au']:
                    val = parameters['au'][openface] / 4 * fac
                    fexmm_parameters['shapekeys'][fexmm] = val
        
        ################ EYES
        
        if (self.send_eyes):
            if ('au' in parameters):
                for openface, fexmm in self.blink.items():
                    blink = parameters['au'][openface] / 3
                    if blink > 1:
                        blink = 1
                    for f in fexmm:
                        fexmm_parameters['shapekeys'][f] = blink
             
            if ('gaze' in parameters):
                gaze = np.array(parameters['gaze'])
                # need to compensate for head pose in gaze estimation
                gaze = np.array([gaze[1], 0, -gaze[0]])
                rot_gaze = Rotation.from_euler('XYZ', gaze)
 
                if (self.send_rotation and 'pose' in parameters):
                    rotation = np.array(parameters['pose'][3:6])
                    head_rotation = Rotation.from_euler('XYZ', rotation)
                    rot_gaze = head_rotation.inv() * rot_gaze   
                 
                fexmm_parameters['eye_gaze'] = rot_gaze.as_euler('XYZ').tolist()
        
        return fexmm_parameters, image


Module = ProcessBase(OpenFaceToFexMMRemapper)
    
