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


    def __init__(self, config, avatar_models, fexmm_gaze_origin, **kwargs):
        '''
        avatar_models: list of collections, where each of collection contains an avatar
        '''

        super().__init__(config, **kwargs)

        self.models = list(avatar_models)
        self.fexmm_gaze_origin = fexmm_gaze_origin
        
        # Store initial values of models
        for collection in self.models:
            name = collection.name
            model = collection.objects[name]
            self.initial_poses[name] = {}
            self.initial_poses[name]['location'] = model.location.copy()
            self.initial_poses[name]['rotation'] = model.rotation_euler.copy()
            self.initial_poses[name]['scale'] = model.scale.copy()
         
            self.initial_aus[name] = {}
            if model.data.shape_keys is not None:
                for key, value in model.data.shape_keys.key_blocks.items():
                    self.initial_aus[name][key] = value.value

        # Set first model as current model
        if len(self.models):
            self.current_model_name = self.models[0].name

        # Show current model
        self.update_visibility()


    def process_control_commands(self, update, receiver_channel = ''):
        if 'avatar_name' in update:
            if update['avatar_name'] in self.models:
                self.current_model_name = update['avatar_name']
            else:
                self.current_model_name = None
            self.update_visibility()
        if 'avatar_scale' in update:
            scalefac = float(update['avatar_scale'])
            self.scale = [scalefac, scalefac, scalefac]
        if 'avatar_gaze_offset_x' in update:
            gaze_offset_x = float(update['avatar_gaze_offset_x'])
            self.fexmm_gaze_origin.location[0] = gaze_offset_x
        if 'avatar_gaze_offset_y' in update:
            gaze_offset_y = float(update['avatar_gaze_offset_y'])
            self.fexmm_gaze_origin.location[1] = gaze_offset_y
        if 'avatar_depth_scale' in update:
            depth_scale = float(update['avatar_depth_scale'])
            self.set_depth_scale(depth_scale) 
        if 'avatar_location_offset' in update:
            location_offset = np.array(update['avatar_location_offset'], dtype = np.float)
            self.set_location_offset(location_offset) 
        if 'avatar_rotation_offset' in update:
            rotation_offset = np.array(update['avatar_rotation_offset'], dtype = np.float)
            self.set_rotation_offset(rotation_offset) 

    def process(self, data, image = None, channel_name = ''):

        if channel_name != 'fexmm_parameters':
            return None, None

        model = self.get_current_model()
        if data and model:
            # get and set for current model only

            model.scale = self.scale
            
            if 'location' in data.keys():
                model.location = np.array(data['location']) + np.array(self.location_offset)
                model.location[1] *= self.depth_scale
                
            if 'rotation' in data.keys():
                model.rotation_euler = np.array(data['rotation']) + np.array(self.rotation_offset)
            
            if model.data.shape_keys is not None and 'shapekeys' in data.keys():
                for key, value in data['shapekeys'].items():
                    if key in model.data.shape_keys.key_blocks.keys():
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
        for model in self.models:
            name = model.name
            if name == self.current_model_name:
                bpy.data.collections[name].hide_viewport = False;
            else:
                bpy.data.collections[name].hide_viewport = True;

    def get_current_model(self):
        for collection in self.models:
            if collection.name == self.current_model_name:
                return collection.objects[self.current_model_name]
        return None

if __name__ == '__main__': 
    
    blender_fexmm_receiver = BlenderFexMMReceiver(modulename = 'blender', face_models_dict = {}, fexmm_gaze_origin = [0,0,0])
    while (1):
        blender_fexmm_receiver.run()
