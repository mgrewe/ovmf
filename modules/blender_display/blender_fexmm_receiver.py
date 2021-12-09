import numpy as np
import bpy
from lib.module_base import ModuleBase


class BlenderFexMMReceiver(ModuleBase):

    models = {}
    current_model_name = None
    #material = None
    initial_poses = {}
    initial_aus = {}
    average = 0
    depth_scale = 1
    location_offset = [0,0,0]
    rotation_offset = [0,0,0]
    scale = [1,1,1]
    fexmm_gaze_origin = None
    last_data = {}


    def __init__(self, config, face_models_dict, fexmm_gaze_origin, **kwargs):

        super().__init__(config, **kwargs)

        if isinstance(face_models_dict,dict):
            self.models = face_models_dict
        else:
            self.models = [ face_models_dict ]

        self.fexmm_gaze_origin = fexmm_gaze_origin
        
        # Store initial values of models

        for name, model in self.models.items():
            self.initial_poses[name] = {}
            self.initial_poses[name]['location'] = model.location.copy()
            self.initial_poses[name]['rotation'] = model.rotation_euler.copy()
            self.initial_poses[name]['scale'] = model.scale.copy()
         
            self.initial_aus[name] = {}
            for key, value in model.data.shape_keys.key_blocks.items():
                self.initial_aus[name][key] = value.value

        # Set first model as current model
        if len(self.models):
            self.current_model_name = list(self.models)[0]

        # Show current model
        self.update_visibility()


    def process_control_commands(self, update, receiver_channel = ''):
        if 'display_avatar' in update:
            if update['display_avatar'] in self.models:
                self.current_model_name = update['display_avatar']
            else:
                self.current_model_name = None
            self.update_visibility()
        if 'display_scale' in update:
            scalefac = float(update['display_scale'])
            self.scale = [scalefac, scalefac, scalefac]
        if 'display_gaze_offset_x' in update:
            gaze_offset_x = float(update['display_gaze_offset_x'])
            self.fexmm_gaze_origin.location[0] = gaze_offset_x
        if 'display_gaze_offset_y' in update:
            gaze_offset_y = float(update['display_gaze_offset_y'])
            self.fexmm_gaze_origin.location[1] = gaze_offset_y
        if 'display_depth_scale' in update:
            depth_scale = float(update['display_depth_scale'])
            self.set_depth_scale(depth_scale) 
        if 'display_location_offset' in update:
            location_offset = np.array(update['display_location_offset'], dtype = np.float)
            self.set_location_offset(location_offset) 
        if 'display_rotation_offset' in update:
            rotation_offset = np.array(update['display_rotation_offset'], dtype = np.float)
            self.set_rotation_offset(rotation_offset) 

    def process(self, data, image = None, channel_name = ''):

        if channel_name != 'fexmm_parameters':
            return None, None

        # 'fexmm_parameters' in self.sock:
        # 'fexmm_animation' in self.sock:

        if data and self.current_model_name:
            # get and set for current model only
            model = self.models[self.current_model_name]

            model.scale = self.scale
            
            if 'location' in data.keys():
                model.location = np.array(data['location']) + np.array(self.location_offset)
                model.location[1] *= self.depth_scale
                
            if 'rotation' in data.keys():
                model.rotation_euler = np.array(data['rotation']) + np.array(self.rotation_offset)
            
            if 'shapekeys' in data.keys():
                for key, value in data['shapekeys'].items():
                    #print('Setting shape key %s to %f' % (key, value))
                    model.data.shape_keys.key_blocks[key].value = value
            
            self.last_data = data

        return data, image

    def set_expression_scale(self, expression_scale = 1):
        self.expression_scale = expression_scale

    def set_pose_scale(self, pose_scale = 1):
        self.pose_scale = pose_scale

    def set_depth_scale(self, depth_scale = 1):
        self.depth_scale = depth_scale
    
    def set_location_offset(self, location = [0,0,0]):
        self.location_offset = location

    def set_rotation_offset(self, rotation = [0,0,0]):
        self.rotation_offset = rotation

    def reset(self):
        for name, model in self.models.items():
            model.location = self.initial_poses[name]['location']
            model.rotation_euler = self.initial_poses[name]['rotation']
            model.scale = self.initial_poses[name]['scale']

            for key, value in self.initial_aus[model].items():
                model.data.shape_keys.key_blocks[key].value = value


    def update_visibility(self):
        print(self.current_model_name)
        for name, model in self.models.items():
            if name == self.current_model_name:
                print(name)
                bpy.data.collections[name].hide_viewport = False;
            else:
                bpy.data.collections[name].hide_viewport = True;

if __name__ == '__main__': 
    
    blender_fexmm_receiver = BlenderFexMMReceiver(modulename = 'blender', face_models_dict = {}, fexmm_gaze_origin = [0,0,0])
    while (1):
        blender_fexmm_receiver.run()
