from pathlib import Path
import sys
import time
import numpy as np
from PIL import Image

dir = str(Path(__file__).resolve().parents[2])
if not dir in sys.path:
    sys.path.append(dir)
from lib.connection import Sender, Receiver
from lib.module_base import loadConfig


class Interface:
    '''
    Python Interface to the Open Virtual Mirror Framework

    Please see psychopy_example.py
    '''

    def __init__(self, view_only = False, debug = True, pipeline=None):
        '''
        Set view_only = True if you want to display the avatar only. 
        Only useful if you want to use multiple Interfaces.

        Set debug = True to print out some infos.
        '''
        self.debug = debug
        config = loadConfig(pipeline=pipeline, module='blender_render_output')
        self.receiver = Receiver(address = config['address'], type='render_output', queue_size=config['queue_size'])['render_output']
        self.view_only = view_only
        if not view_only:
            self.commands = Sender(address = config['control_commands'])
            # Need some time to init...
            time.sleep(1)

    def check_view_only(self):
        if self.view_only:
            if self.debug:
                print("Avatar class is view-only. Can't change parameters.")
            return True

    def set_parameter(self, params_dict):
        '''
        Set generic parameters in form of a dictionary. 
        Look at the modules for supported parameters.
        '''
        if self.debug:
            print("Parameter: " + str(params_dict))
        self.commands.send(params_dict)

    def set_delay(self, delay_seconds = 0):
        '''
        Set the avatar motion delay in seconds
        '''

        if self.check_view_only():
            return

        params = {
            'delay_ms' : float(delay_seconds) * 1000
        }
        self.set_parameter(params)

    def set_avatar(self, avatar_name = 'FexMM'):

        if self.check_view_only():
            return

        params = {
            'avatar_name' : avatar_name
        }
        self.set_parameter(params)

    def set_scale(self, avatar_scale = 1.0):
        '''
        set avatar uniform scale in 3d
        '''

        if self.check_view_only():
            return

        params = {
            'avatar_scale' : avatar_scale
        }
        self.set_parameter(params)

    def set_depth_scale(self, avatar_depth_scale = 1.0):
        '''
        set avatar depth scale factor
        '''

        if self.check_view_only():
            return

        params = {
            'avatar_depth_scale' : avatar_depth_scale
        }
        self.set_parameter(params)

    def set_location_offset(self, avatar_location_offset = [0,0,0]):
        '''
        set avatar location offset (before application of scale factor)
        '''

        if self.check_view_only():
            return

        params = {
            'avatar_location_offset' : avatar_location_offset
        }
        self.set_parameter(params)

    def set_rotation_offset(self, avatar_rotation_offset = [0,0,0]):
        '''
        set avatar rotation offset (before application of scale factor)
        '''

        if self.check_view_only():
            return

        params = {
            'avatar_rotation_offset' : avatar_rotation_offset
        }
        self.set_parameter(params)

    def set_gaze_offset(self, gaze_offset = [0,0] ):
        '''
        set avatar gaze offset relative to the screen midpoint in blender units
        '''

        if self.check_view_only():
            return

        params = {
            'avatar_gaze_offset_x' : gaze_offset[0],
            'avatar_gaze_offset_y' : gaze_offset[1]
        }
        self.set_parameter(params)

    def receive_image(self):
        return self.receiver.receive(block = False)
   
    def receive_and_set_image(self, imgStim = None, adjust_render_size = True, fill_color = 'black'):
        '''
        Receives a new rendered image if available (non-blocking) and sets it to the Psychopy
        image stimulus (imgStim). 
        If adjust_render_size is True, the size of the rendered image 
        will be adjusted to fit into imgStim. Aspect ratio is kept and fill_color is used to 
        fill-in the border area. 
        Otherwise, the size of imgStim is adjusted to the size of the rendered image.
        '''
        if imgStim is not None:
            data, image = self.receive_image()

            # SLOW. TODO: Improve and fix if image exceeds ImageStim size
            if image is not None:
                if adjust_render_size:
                    img = Image.fromarray(image).convert('RGBA')
                    size = (int(imgStim.size[0]),int(imgStim.size[1]))
                    img.thumbnail(size)
                    image = Image.new('RGBA', size, fill_color)   
                    size = (int((imgStim.size[0] - img.size[0])/2),
                        int((imgStim.size[1] - img.size[1])/2))
                    image.paste(img, size)
                    image = image.convert('RGB')
                    image = np.asarray(image)
                    image = image / 255
                else:
                    imgStim.size = (image.shape[1] , image.shape[0])
                    image = image / 255
                imgStim.setImage(image)
            return data

        return None

       
    def receive_and_convert_image(self):
        '''
        Receives a new rendered image if available (non-blocking) and sets it to the numpy array. 
        '''
        data, im = self.receive_image()
        if data is None or im is None:
            return None, None

        im = im / 255
        return data, im
