from pathlib import Path
import sys
import time
import numpy as np
from PIL import Image
sys.path.append(str(Path(__file__).parents[2] / 'lib'))
from connection import Sender, Receiver, getAddress

class Interface:
    '''
    This class provides an interface to the 
    face_vr framework developed at ZIB.

    Contact: Martin Grewe (grewe@zib.de)

    Please see display_avatar*.py for examples how to use the interface 
    in your Psychopy experiments.
    '''

    def __init__(self, view_only = False, debug = True):
        '''
        Set view_only = True if you want to display the avatar only. 
        This is usefull to allow control from another process.

        Set debug = True to print out some infos.
        '''
        self.debug = debug
        sock_address = getAddress('blender_render_output', None)[0]
        print(sock_address)
        self.receiver = Receiver(address = sock_address,queue_size=1,drop_images_before_processing=False)[sock_address]
        self.view_only = view_only
        if not view_only:
            sock_address = getAddress('control_commands', None)[0]
            self.commands = Sender(address = sock_address)
            # Need some time to init...
            time.sleep(1)

    def check_view_only(self):
        if self.view_only:
            if self.debug:
                print("Avatar class is view-only. Can't change parameters.")
            return True

    def set_parameter(self, params_dict):
        if self.debug:
            print("Parameter: " + str(params_dict))
        self.commands.send(params_dict)


    def set_delay(self, delay = 0):
        '''
        Set the avatar motion delay in millisecs
        '''

        if self.check_view_only():
            return

        params = {
            'buffer_delay' : float(delay)
        }
        self.set_parameter(params)

    def set_avatar(self, avatar = 'female'):

        if self.check_view_only():
            return

        params = {
            'display_avatar' : avatar
        }
        self.set_parameter(params)


    def set_scale(self, scale = 1.0):
        '''
        set avatar uniform scale in 3d
        '''

        if self.check_view_only():
            return

        params = {
            'display_scale' : scale
        }
        self.set_parameter(params)

    def set_depth_scale(self, depth_scale = 1.0):
        '''
        set avatar depth scale factor
        '''

        if self.check_view_only():
            return

        params = {
            'display_depth_scale' : depth_scale
        }
        self.set_parameter(params)

    def set_location_offset(self, location_offset = [0,0,0]):
        '''
        set avatar location offset (before application of scale factor)
        '''

        if self.check_view_only():
            return

        params = {
            'display_location_offset' : location_offset
        }
        self.set_parameter(params)

    def set_rotation_offset(self, rotation_offset = [0,0,0]):
        '''
        set avatar rotation offset (before application of scale factor)
        '''

        if self.check_view_only():
            return

        params = {
            'display_rotation_offset' : rotation_offset
        }
        self.set_parameter(params)

    def set_gaze_offset(self, offset = [0,0] ):
        '''
        set avatar gaze offset relative to the screen midpoint in blender units
        '''

        if self.check_view_only():
            return

        params = {
            'display_gaze_offset_x' : offset[0],
            'display_gaze_offset_y' : offset[1]
        }
        self.set_parameter(params)

    def set_expression_scale(self, expression_scale = 1.0):
        '''
        set avatar expression scale factor, e.g. for damping or amplification.
        expression_scale = 0 completely cancels au activation.
        '''

        if self.check_view_only():
            return

        params = {
            'fexmm_expression_scale' : expression_scale
        }
        self.set_parameter(params)

        
    def set_combiner_channel(self, channel = None):
        '''
        set avatar pose scale factor, e.g. for damping or amplification.
        pose_scale = 0 completely cancels poses
        '''

        if self.check_view_only():
            return

        params = {
            'combiner_active_receiver_channel' : channel
        }
        self.set_parameter(params)

    def set_pose_scale(self, pose_scale = 1.0):
        '''
        set avatar pose scale factor, e.g. for damping or amplification.
        pose_scale = 0 completely cancels poses
        '''

        if self.check_view_only():
            return

        params = {
            'fexmm_pose_scale' : pose_scale
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

            # VERY SLOW. TODO: Improve and fix if image exceeds ImageStim size
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
