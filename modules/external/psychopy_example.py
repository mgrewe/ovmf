import sys
from pathlib import Path

# THIS PATH NEEDS ADJUSTMENT TO YOUR SETUP
dir = str(Path(__file__).resolve().parents[2])
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# E.G. dir = '/path_to_the_framework/face_vr/'

if not dir in sys.path:
    sys.path.append(dir)
import modules.external.ovmf as ovmf
from lib.module_base import ProcessBase


class Proc(ProcessBase):
    def main(self):
        from psychopy import visual, core

        vm_interface = ovmf.Interface(view_only=False, pipeline=self.config['pipeline'] if hasattr(self, 'config') else None)

        win = visual.Window(
            size=[1088, 728],
            units="pix",
            fullscr=False,
            gammaErrorPolicy = 'ignore',
            waitBlanking=False)

        img = visual.ImageStim(win, units = 'pix')
        img.size = [640, 480]
        img.setAutoDraw(False)
        img.interpolate = True

        vm_interface.set_delay(0)

        while True:

            vm_interface.receive_and_set_image(img,fill_color='gray')

            # Trigger redraw
            img.draw()
            win.flip()

Module = Proc(None)


if __name__ == "__main__":
    Module.main()
