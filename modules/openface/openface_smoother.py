import sys
import pathlib as pl
import numpy as np
from scipy.spatial.transform import Rotation as R

dir = str(pl.Path(__file__).resolve().parents[2])
if not dir in sys.path:
    sys.path.append(dir)
from lib.module_base import ModuleBase, ProcessBase


class OpenFaceSmoother(ModuleBase):
    # Currently, a lower smoothing factor actually means more smoothing, which is little intuitive.
    # TODO: Invert smoothing values
    # TODO: Use time for determining smoothing factor, since it currenty depends on fps.
    
    smoothing = {
        'au': 0.4,
        'pose_rotation': 0.5,
        'pose_location': 0.5,
        'gaze': 0.2,
        }

        # OpenFace AU, FexMM Shapekey
    au_smoothing = {
            # # Eye units
            # 'AU01':1,
            # 'AU02':1,
            # 'AU04':1,
             'AU05':1/3,
            # 'AU06':1,
            # 'AU07':2,
            # # Nose wrinkler
            # 'AU09':1,
            # # Mouth units
            # 'AU10': 1,
            # 'AU12': 1,
            # 'AU14': 1,
            # 'AU15': 1,
            # 'AU17': 1,
            # 'AU20': 1,
            # 'AU23': 1,
            # 'AU25': 1,
            'AU26' : 2/3
            }

    dynamic_au_smoothing = True

    # clamp rotation within interval
    restrict_pose = False
    rotation_interval = np.pi/8

    # damp au's with higher head rotation
    smooth_au_by_pose = True
    rotation_smooth_interval = np.pi/5
    
    exclude_au_from_smoothing = ['AU45']
    
    last_data = None

    def process_control_commands(self, update, receiver_channel = ''):
        if not update:
            return
        
        if 'smoothing_factor_au' in update:
            self.smoothing['au'] = float(update['smoothing_factor_au'])

        if 'smoothing_factor_pose' in update:
            self.smoothing['pose_rotation'] = float(update['smoothing_factor_pose'])
            self.smoothing['pose_location'] = float(update['smoothing_factor_pose'])

    def process(self, data, image, receiver_channel):
        # data = self.receiver['tracker_parameters'].receive()
        
        au_fac = self.smoothing['au']
        pose_rotation_fac = self.smoothing['pose_rotation']
        pose_location_fac = self.smoothing['pose_location']
        gaze_fac = self.smoothing['gaze']

        
        if (self.last_data == None):
            self.last_data = data
            return data, image

        #print(self.last_data['timestamp'] - data['timestamp'])

        if ('au' in data):
            if (self.smooth_au_by_pose):
                # determine maximum rotational compoent
                dynamic_smoothing_fac = np.amax(np.abs(np.array(data['pose'][3:5])))
                dynamic_smoothing_fac /= self.rotation_smooth_interval
                dynamic_smoothing_fac = np.min([0.95,dynamic_smoothing_fac])
                dynamic_smoothing_fac = 1 - np.float_power(dynamic_smoothing_fac,2)
            else:
                dynamic_smoothing_fac = 1

            
            for key, value in data['au'].items():
                if key in self.exclude_au_from_smoothing:
                    continue

                if (key == 'AU26'):
                    # Some tuning to keep the mouth closed in rest, an offset seems to be estimated
                    value -= 1
                    value = max(0,value)
                    #value *= 4/3
                    #val = min(1,val)

                value *= dynamic_smoothing_fac
                if key in self.au_smoothing:
                    au_fac_ind = au_fac * self.au_smoothing[key]
                else:
                    au_fac_ind = au_fac
                data['au'][key] = au_fac_ind * value + (1 - au_fac_ind) * self.last_data['au'][key]
                

        if ('pose' in data):
            if (self.restrict_pose):
                data['pose'][3:5]=np.clip(data['pose'][3:5],-self.rotation_interval,self.rotation_interval)

            pose = data['pose']
            pose[3:6] = pose_rotation_fac *  np.array(data['pose'])[3:6] + (1 - pose_rotation_fac) * np.array(self.last_data['pose'])[3:6]
            pose[0:3] = pose_location_fac *  np.array(data['pose'])[0:3] + (1 - pose_location_fac) * np.array(self.last_data['pose'])[0:3]
            data['pose'] = pose


        
        if ('gaze' in data):
            gaze  = gaze_fac *  np.array(data['gaze']) + (1 - gaze_fac) * np.array(self.last_data['gaze'])
            data['gaze'] = gaze.tolist()


        self.last_data = data

        return data, image


Module = ProcessBase(OpenFaceSmoother)
