from psychopy import visual, core, event
import ovmf

# Create the virtual mirror interface, please copy as is
vm_interface = ovmf.Interface(view_only=False, pipeline=self.config['pipeline'] if hasattr(self, 'config') else None)

# Create PsychoPy window and image stimulus
win = visual.Window(
    size=[1088, 728],
    units="pix",
    fullscr=False,
    gammaErrorPolicy = 'ignore',
    waitBlanking=False)

while True:

    message = visual.TextStim(win, text='Welcome to the OVMF!')
    message.draw()
    win.flip()
    while True:
        # Get keys pressed by the participant
        keys = event.getKeys()
        
        # If the participant strokes "q"
        if len(keys) > 0:
            # just quit the program
            break

    img = visual.ImageStim(win, units = 'pix')
    img.size = [1080, 720]
    # img.setAutoDraw(True)

    # Prepare the first stimulus
    timer = core.CountdownTimer(5000)
    # Run forever
    while timer.getTime() > 0:
        # Receive and set image
        vm_interface.receive_and_set_image(img, fill_color='gray')
        # data, image = vm_interface.receive_image()
        # if (image is not None):
        #     img.setImage(image)
        img.draw()

        win.flip()
