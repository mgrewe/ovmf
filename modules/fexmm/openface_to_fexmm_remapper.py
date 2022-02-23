import copy
import numpy as np
from scipy.spatial.transform import Rotation

from lib.module_base import ModuleBase, ProcessBase
from lib.auxiliary import get_time_ms


class OpenFaceToFexMMRemapper(ModuleBase):
    
    send_aus = True
    send_location = True
    send_rotation = True
    send_eyes = True
    expression_scale = 1
    global_expression_scale = 2
    pose_scale = 1
    

    # # OpenFace AU, FexMM Shapekey
    # catch_au = {
    #         # Eye units
    #         'AU01': ('AU_1', 1),
    #         'AU02': ('AU_2', 1),
    #         'AU04': ('AU_4', 1),
    #         'AU05': ('AU_5', 1),
    #         'AU06': ('AU_6', 1),
    #         'AU07': ('AU_7', 1),
    #         # Nose wrinkler
    #         'AU09': ('AU_9', 1),
    #         # Mouth units
    #         'AU10': ('AU_10_lip_only', 1),
    #         'AU12': ('AU_12', 1),
    #         'AU14': ('AU_14', 1),
    #         'AU15': ('AU_15', 1),
    #         'AU17': ('AU_17', 1),
    #         'AU20': ('AU_20', 1),
    #         'AU23': ('AU_23', 1),
    #         'AU25': ('AU_25', 1),
    #         'AU26' : ('AU_26', 1)
    #         #'AU28' NA
    #         }
    
    # blink = {'AU45': ['au_43l', 'au_43r'] }
    # blink = {'AU45': ['AU_43'] }

        # OpenFace AU, FexMM Shapekey
    catch_au = {
            # Eye units
            'AU01': ('AU_1', 0.31618408694746414 * 2),
            'AU02': ('AU_2', 1.5419858974546923 * 0.7),
            'AU04': ('AU_4', 0.9137313611096083 * 1.25),
            'AU05': ('AU_5', 1.206789360737912),
            'AU06': ('AU_6', 0.9624696090691882),
            'AU07': ('AU_7', 0.5612491367059758),
            # Nose wrinkler
            'AU09': ('AU_9', 0.6484832148362141),
            # Mouth units
            'AU10': ('AU_10_lip_only', 0.7852077705230291 * 0.5),
            'AU12': ('AU_12', 0.4286397565172854 * 1),
            'AU14': ('AU_14', 0.40374317524332903),
            'AU15': ('AU_15', 0.5320387478992187 * 3.0),
            'AU17': ('AU_17', 0.7224931077716031),
            'AU20': ('AU_20', 0.46211089040278813 * 2.5),
            'AU23': ('AU_23', 0.2935380112023344),
            'AU25': ('AU_25', 1.1110248765726423),
            'AU26' : ('AU_26', 0.5467196743826498 * 1.5)
            #'AU28' NA
            }
                    # OpenFace AU, FexMM Shapekey
    
    blink = {'AU45': ['au_43l', 'au_43r'] }
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
        if 'fexmm_expression_scale' in update:
            self.expression_scale = np.float(update['fexmm_expression_scale'])
        if 'fexmm_pose_scale' in update:
            self.pose_scale = np.float(update['fexmm_pose_scale'])


    def process(self, data, image, channel_name):
        parameters = data
        fexmm_parameters = copy.deepcopy(parameters)

        ################################
        ############## LOCATION
        ################################
        
        if (self.send_location and 'pose' in parameters):
            location = np.array(parameters['pose'][0:3])
            # Scale to blender units
            location[2] -= 700
            location *= 0.01 * self.pose_scale
            #translation = [-translation[0] - 8, translation[2] - 90, -translation[1] - 5]
            
            fexmm_parameters['location'] = [-location[0], location[2], -location[1]]

        ################################
        ############## ROTATION
        ################################

        if (self.send_rotation and 'pose' in parameters):        
            rotation = np.array(parameters['pose'][3:6])
            rotation = np.array([rotation[0], -rotation[2], rotation[1]]) * self.pose_scale
            # Need to adjust rotation a little bit
            # tilt, roll, yaw
            #rotation += np.array([0.1,-0.05,0.12])        
            fexmm_parameters['rotation'] = rotation.tolist()

        ################################
        ############### AU's
        ################################
        if (self.send_aus and 'au' in parameters):
            fexmm_parameters['shapekeys'] = {}
            for openface, (fexmm, fac) in self.catch_au.items():
                if openface in parameters['au']:
                    val = parameters['au'][openface] / 5 * fac * self.expression_scale * self.global_expression_scale
                    #val /= 4
                    # if (openface == 'AU26'):
                    #     # Some tuning to keep the mouth closed in rest, an offset seems to be estimated
                    #     val -= 0.3
                    #     val = max(0,val)
                        #val *=2
                        #val = min(1,val)
                    fexmm_parameters['shapekeys'][fexmm] = val
        
        ################################    
        ################ EYES
        ################################
        
        if (self.send_eyes):
            if ('au' in parameters):
                for openface, fexmm in self.blink.items():
                    # blink = min(1, parameters['au'][openface] / 4 / 2 )
                    # blink = 0.65 * (blink > 0.38)
                    blink = parameters['au'][openface] / 3
                    if blink > 1:
                        blink = 1
                    #blink = 0.65 * (blink > 0.38)
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
    
