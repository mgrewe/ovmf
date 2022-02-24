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
from lib.auxiliary import get_time_ms

class BlenderAvatar(ModuleBase):

    avatars = bpy.data.collections['Avatars'].children

    gaze_origin = bpy.data.objects['Avatar_Gaze']

    receivers = []

    render_output = None

    last_data = {}
    

    def __init__(self, config, **kwargs):

        super().__init__(config, **kwargs)

        rv_config = config
        rv_config['use_sockets'] = False
        self.receivers.append(BlenderFexMMReceiver(rv_config, self.avatars, self.gaze_origin))
        ro_config = loadConfig(config['pipeline'], 'blender_render_output')
        ro_config = {**config, **ro_config}
        self.render_output = BlenderRenderOutput(ro_config, start_sender_thread=True)
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


# Largely based on this solution
# https://blender.stackexchange.com/a/231881
class StreamingOperator(bpy.types.Operator):
    """Operator which streams the 3D view over the network"""
    bl_idname = "view3d.stream_view"
    bl_label = "Streaming Operator"

    # TODO: expose as parameter
    pause_ms = 5
    last_rendering = get_time_ms()


    def draw(self, context):
        if (get_time_ms() - self.last_rendering) > self.pause_ms:
            self.blender_receiver.update()
            self.last_rendering = get_time_ms()


    def invoke(self, context, event):
        print("Starting streaming operator...")

        argv = None
        if '--' in sys.argv:
            argv = sys.argv[sys.argv.index('--') + 1:]
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', '--pipeline', required=True)
        parser.add_argument('-c', '--config', required=True)
        args, _ = parser.parse_known_args(argv)
        config = json.loads(args.config)

        self.blender_receiver = BlenderAvatar(config)

        self._handle_3d = bpy.types.SpaceView3D.draw_handler_add(StreamingOperator.draw, (self, context), 'WINDOW', 'PRE_VIEW')

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def modal(self, context, event):
        if event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_3d, 'WINDOW')
            print("Stopping streaming operator")
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

class TriggerRedrawOperator(bpy.types.Operator):
    """Redraw timer"""
    bl_idname = "view3d.redraw_timer"
    bl_label = "Timer to Trigger Redraw"

    _timer = None
    

    def modal(self, context, event):
        if event.type in {'ESC'}:
            print("Stopping redraw trigger operator...")
            wm = context.window_manager
            wm.event_timer_remove(self._timer)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
            area.tag_redraw()

        return {'PASS_THROUGH'}

    def execute(self, context):
        print("Starting redraw trigger operator...")

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.005, window=context.window)
        wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}
        


def register():
    bpy.utils.register_class(StreamingOperator)
    bpy.utils.register_class(TriggerRedrawOperator)


def unregister():
    bpy.utils.unregister_class(StreamingOperator)
    bpy.utils.unregister_class(TriggerRedrawOperator)


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
   
    register()

    bpy.ops.view3d.redraw_timer()
    bpy.ops.view3d.stream_view('INVOKE_DEFAULT')
    

