import argparse, json
import sys, pathlib
import bpy

dir = str(pathlib.Path(__file__).resolve().parent)
if not dir in sys.path:
    sys.path.append(dir)
dir = str(pathlib.Path(dir).resolve().parents[1])
if not dir in sys.path:
    sys.path.append(dir)
from blender_fexmm_receiver import BlenderFexMMReceiver
from blender_render_output import BlenderRenderOutput
from lib.module_base import ModuleBase, loadConfig


class BlenderReceiver(ModuleBase):

    avatars = {
        '3D1001': bpy.data.objects['3D1001'],
        }

    gaze_origin = bpy.data.objects['Avatar_Gaze']

    blender_fexmm_receiver = None

    receivers = []

    render_output = None

    last_data = {}
    

    def __init__(self, config, blender_render_context, **kwargs):

        super().__init__(config, **kwargs)

        rv_config = config
        rv_config['use_sockets'] = False
        self.receivers.append(BlenderFexMMReceiver(rv_config, self.avatars, self.gaze_origin))
        ro_config = loadConfig(config['pipeline'], 'blender_render_output')
        ro_config = {**config, **ro_config}
        self.render_output = BlenderRenderOutput(ro_config, blender_render_context,start_sender_thread=True)
        self.render_output.start_streaming()

        self.receivers.append(self.render_output)
        sys.stdout.flush()

    def __del__(self):
        self.render_output.stop_streaming()

    def process_control_commands(self, commands, receiver_channel = ''):
        for r in self.receivers:
            r.process_control_commands(commands, receiver_channel)

    def process(self, data, image, receiver_channel = ''):
        for r in self.receivers:
            data, image = r.process_and_measure(data,image, receiver_channel)

        self.last_data = data
        return data, image


class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None
    

    def modal(self, context, event):

        if event.type == 'TIMER':
            self.blender_receiver.update()

        return {'PASS_THROUGH'}

    def execute(self, context):
        print("Starting operator....")

        argv = None
        if '--' in sys.argv:
            argv = sys.argv[sys.argv.index('--') + 1:]
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', '--pipeline', required=True)
        parser.add_argument('-c', '--config', required=True)
        args, _ = parser.parse_known_args(argv)
        config = json.loads(args.config)

        self.blender_receiver = BlenderReceiver(config, context)
        
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.001, window=context.window)
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}
        

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        del self.blender_receiver
        self.blender_receiver = None


def register():
    bpy.utils.register_class(ModalTimerOperator)


def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)

def setup():    
    
    register()

    bpy.ops.wm.modal_timer_operator()


if __name__ == "__main__":

    # Get first 3d viewport
    area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')

    # Get first space
    space = area.spaces[0]

    # Set to first camera view
    space.region_3d.view_perspective = 'CAMERA'

    # Do not show gizmo in the upper right corner
    space.show_gizmo = False 

    # Set shading
    space.shading.type = 'RENDERED'
    #space.shading.type = 'MATERIAL'
   
    setup()

