from psychopy import visual, core
import ovmf

vm_interface = ovmf.Interface(view_only=False)

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

vm_interface.set_avatar('FexMM') 
vm_interface.set_delay(0)

while True:

    vm_interface.receive_and_set_image(img)

    # Trigger redraw
    img.draw()
    win.flip()