from psychopy import visual, core
import ovmf


# Create the virtual mirror interface
vm_interface = ovmf.Interface()
# Set 
vm_interface.set_delay(2)

win = visual.Window(
    size=[1088, 728],
    units="pix",
    fullscr=False,
    gammaErrorPolicy = 'ignore',
    waitBlanking=False)

img = visual.ImageStim(win, units = 'pix')
img.size = [640, 480]
img.setAutoDraw(True)

while True:

    vm_interface.receive_and_set_image(img)

    # Trigger redraw
    img.draw()
    win.flip()