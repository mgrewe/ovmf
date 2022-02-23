import numpy as np

from lib.module_base import ModuleBase, ProcessBase


class OpenFaceSmoother(ModuleBase):
    # Smoothing factor between 0 (no smoothing) and 1 (max smoothing, i.e., no movement)

    # TODO: Use time for determining smoothing factor, since it currenty depends on fps.
    
    # movement, smoothing factor (0,1)
    smoothing = {
        'au': 0.6,
        'pose_rotation': 0.5,
        'pose_location': 0.5,
        'gaze': 0.8,
        }

    # Individual smoothing factors for Action Units
    # OpenFace AU, smoothing factor (0,1)
    au_smoothing = {
            #  'AU05':2/3,
            # 'AU26' : 1/3
            }

    # Avoid too large rotations by
    # clamping to interval
    restrict_pose = False
    rotation_interval = np.pi/8

    # Avoid strange movements with large rotations due to tracking errors by
    # damping AUs with higher head rotation
    smooth_au_by_pose = True
    rotation_smooth_interval = np.pi/5
    
    # Specify AUs which are never smoothed
    exclude_au_from_smoothing = []
    
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
        
        au_fac = self.smoothing['au']
        pose_rotation_fac = self.smoothing['pose_rotation']
        pose_location_fac = self.smoothing['pose_location']
        gaze_fac = self.smoothing['gaze']

        
        if (self.last_data == None):
            self.last_data = data
            return data, image

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
                data['au'][key] = (1 - au_fac_ind) * value + au_fac_ind * self.last_data['au'][key]
                

        if ('pose' in data):
            if (self.restrict_pose):
                data['pose'][3:5]=np.clip(data['pose'][3:5],-self.rotation_interval,self.rotation_interval)

            pose = data['pose']
            pose[3:6] = (1 - pose_rotation_fac) *  np.array(data['pose'])[3:6] + pose_rotation_fac * np.array(self.last_data['pose'])[3:6]
            pose[0:3] = (1 - pose_location_fac) *  np.array(data['pose'])[0:3] + pose_location_fac * np.array(self.last_data['pose'])[0:3]
            data['pose'] = pose


        
        if ('gaze' in data):
            gaze  = (1 - gaze_fac) *  np.array(data['gaze']) + gaze_fac * np.array(self.last_data['gaze'])
            data['gaze'] = gaze.tolist()


        self.last_data = data

        return data, image


Module = ProcessBase(OpenFaceSmoother)
