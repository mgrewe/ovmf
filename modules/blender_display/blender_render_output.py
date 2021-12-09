from threading import Thread, Lock, Event
from copy import copy
import numpy as np
import bpy, gpu, bgl
from lib.module_base import ModuleBase
from lib.auxiliary import get_time_ms

class BlenderRenderOutput(ModuleBase):
    sender = None
    offscreen = None
    buffer = None
    running = False
    image = None
    lock = Lock()
    data = None
    new_image = Event()
    blender_render_context = None

    def __init__(self, config, blender_render_context, start_sender_thread = False, **kwargs):
        self.blender_render_context = blender_render_context
        self.start_sender_thread = start_sender_thread
        self.area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
        super().__init__(config, **kwargs)

    def process(self, data, image, receiver_channel = ''):
        data, image = self.take_snapshot(self.blender_render_context, data, False)
        if not self.start_sender_thread:
            self.send_image()
        return data,image

    def process_and_measure(self, data, image, receiver_channel = ''):
        data, image = self.take_snapshot(self.blender_render_context, data, True)
        if not self.start_sender_thread:
            self.send_image()
        return data,image

    def start_streaming(self):
        print("Start streaming...")

        if self.start_sender_thread:
            print("Using async sender thread.")
            self.sender_thread = Thread(target = self.run, args=(self,))
            self.running = True
            self.sender_thread.start()  

    def stop_streaming(self):
        print("Stop streaming...", flush=True)
        if self.start_sender_thread:
            self.running = False
            self.sender_thread.join()
        if self.sender:
            del self.sender
            self.sender = None
        
    @staticmethod
    def run(self):
        while (self.running):
            self.send_image()

    def send_image(self):
        if not self.new_image.wait(timeout = 0.1):
            return
        #data, image = self.buffer_queue.get(block=True, timeout=0.01)
        self.lock.acquire()
        self.sender.send(msg = self.data, img = self.image)
        self.new_image.clear()
        self.lock.release()
    
    # def set_size(self, size=None):
    #     if size is None:
    #         self.offscreen = None
    #     else:
    #         print("Setup offscreen with size ",size[0], size[1])
    #         self.offscreen = gpu.types.GPUOffScreen(size[0], size[1])
    #         self.image = np.zeros([size[1], size[0], 4],dtype=np.uint8)
    #         self.buffer = bgl.Buffer(bgl.GL_BYTE, self.image.shape, self.image)

    def ensure_buffer(self, context):

        if (self.offscreen == None):
            # Determine window size from viewport
            #area = context.area

            width = self.area.width
            height = self.area.height

            # viewport = bgl.Buffer(bgl.GL_INT, 4)
            # bgl.glGetIntegerv(bgl.GL_VIEWPORT, viewport)

            # width = int(viewport[2]/2)
            # height = int(viewport[3]/2)

            if (self.image is None or self.image.shape[0:2] != (height, width)):
                self.image = np.zeros([height, width, 4],dtype=np.uint8)
                self.buffer = bgl.Buffer(bgl.GL_BYTE, self.image.shape, self.image)

    def take_snapshot(self, context, data, measure_time = True):

        start = get_time_ms()

        self.area.tag_redraw()

        scene = context.scene
        camera = scene.camera

        self.ensure_buffer(context)
        (height, width) = self.image.shape[0:2]

        
        # We currently to not support offscreen rendering.
        # # TODO: REIMPLEMENt OFFSCREEN RENDERInG
        
        # if self.offscreen:

        #     with self.offscreen.bind():

        #         modelview_matrix = camera.matrix_world.inverted()
        #         projection_matrix = camera.calc_matrix_camera(context.evaluated_depsgraph_get(), x=width, y=height)

        #         self.offscreen.draw_view3d(
        #             scene,
        #             context.view_layer,
        #             context.space_data,
        #             context.region,
        #             modelview_matrix,
        #             projection_matrix)


        #         bgl.glBindTexture(bgl.GL_TEXTURE_2D, self.offscreen.color_texture);
        #         self.lock.acquire()
        #         bgl.glGetTexImage(bgl.GL_TEXTURE_2D,0,bgl.GL_RGBA, bgl.GL_UNSIGNED_BYTE, self.buffer)
        #         self.lock.release()

        # else:

        bgl.glReadBuffer(bgl.GL_FRONT)
        self.lock.acquire()
        bgl.glReadPixels(0, 0, width, height, bgl.GL_RGBA, bgl.GL_UNSIGNED_BYTE, self.buffer)
            

        end = get_time_ms()

        if data is None:
            data = {}
            
        if measure_time & ('time_statistics' in data.keys()):
            data['time_statistics']['blender_render_output'] = {'start_time': start, 'end_time': end}

        self.data = copy(data)
        self.new_image.set()
        self.lock.release()

        return data, self.image
