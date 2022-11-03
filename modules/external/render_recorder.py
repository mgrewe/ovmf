import cv2
import ovmf
import pathlib
# Create the virtual mirror interface, please copy as is
vm_interface = ovmf.Interface(view_only=False, pipeline=self.config['pipeline'] if hasattr(self, 'config') else None)

output_dir = '/tmp/ovmf_render/'
pathlib.Path(output_dir).mkdir(exist_ok=True)
count = 0

while True:
    # Receive and set image
    data, img = vm_interface.receive_image()
    if (img is not None):
        img = cv2.flip(img, 0)
        img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
        filename = output_dir + "{:05d}.jpg".format(count)
        cv2.imwrite(filename, img)
        count += 1
    
q