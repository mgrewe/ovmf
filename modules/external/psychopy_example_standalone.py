#################################################
# COPY THESE LINES.....
ovmf_dir='/home/bzfgrewe/projects/ovmf'
#         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# This path needs adjustment!
# Replace it with the directory where the ovmf
# has been installed.
import sys
sys.path.append(ovmf_dir)
import ovmf
# ...UNTIL HERE
#################################################

from psychopy import visual, core

# Create the virtual mirror interface
vm_interface = ovmf.Interface()
# Set delay in seconds
vm_interface.set_delay(0)

# Create PsychoPy window and image stimulus
win = visual.Window(
    size=[1088, 728],
    units="pix",
    fullscr=False,
    gammaErrorPolicy = 'ignore',
    waitBlanking=False)
img = visual.ImageStim(win, units = 'pix')
img.size = [640, 480]
img.setAutoDraw(True)

# Run forever
while True:
    # Receive and set image
    vm_interface.receive_and_set_image(img, fill_color='gray')
    win.flip()
