from psychopy import visual, core
import ovmf

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
vm_interface.set_parameter({
    'expressionscaling_au_scale':0
})

while True:

    vm_interface.receive_and_set_image(img,fill_color='gray')

    # Trigger redraw
    img.draw()
    win.flip()
