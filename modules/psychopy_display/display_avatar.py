from psychopy import visual, core
import sys
from pathlib import Path
# THIS PATH NEEDS ADJUSTMENT TO YOUR SETUP
sys.path.append(Path(__file__).resolve())
#               ^^^^^^^^^^^^^^^^^^^^^^^^
# E.G. sys.path.append('/path_to_the_framework/face_vr/modules/psychopy_display/')

import ovmf
import numpy as np
import time
import random
import sys


if __name__ == "__main__":

    vm_interface = ovmf.Interface(view_only=False)

    win = visual.Window(
        size=[1088, 728],
        units="pix",
        fullscr=False,
        gammaErrorPolicy = 'ignore')

    img = visual.ImageStim(win, units = 'pix')
    img.size = [640, 480]
    img.setAutoDraw(False)
    img.interpolate = True

    # Currently possible in the Oldenburg study 1: '3D1001', '3D1012', '1004', '1034', '1046'
    vm_interface.set_avatar('3D1001') 
    vm_interface.set_delay(0)
    vm_interface.set_expression_scale(1)

    while (1):

        vm_interface.receive_and_set_image(img)

        # Trigger redraw
        img.draw()
        win.flip()