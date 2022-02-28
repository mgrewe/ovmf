import time
from threading import Thread, Lock, Event
from platform import system as pf_system
import cv2

from lib.auxiliary import get_time_ms
from lib.module_base import ModuleBase, ProcessBase

USE_SELF_ESTIMATED_TIMESTAMP = True

# TODO: Print out FOURCC code instead of number

class WebcamInput(ModuleBase):

    camera = None
    scale = 1
    delay = 0
    last_send = get_time_ms()
    running = False
    image = None
    timestamp = None
    new_image = Event()
    lock = Lock()


    # fourcc = 'YUYV' OR 'MJPG'
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

        if pf_system() == 'Windows': # windows (including MSYS2)
            self.camera = cv2.VideoCapture(int(config["device"]), cv2.CAP_DSHOW)
        elif pf_system() == 'Linux':
            self.camera = cv2.VideoCapture(int(config["device"]), cv2.CAP_V4L2)
        else:
            raise Exception('Operating System not supportet.')
        # Set FPS twice to make sure it is correctly set on different systems
        self.camera.set(cv2.CAP_PROP_FPS, int(config["fps"]))	# on some systems fps must be set before fourcc
        self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*config["fourcc"][:4]))
        self.camera.set(cv2.CAP_PROP_FPS, int(config["fps"]))	# on some systems fps must be set before fourcc
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, int(config["width"]))
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, int(config["height"]))
        self.scale = float(config["scale"])
        self.delay = float(config["delay"])

        self.intrinsics = WebcamInput.guessIntrinsics(self.scale * self.camera.get(cv2.CAP_PROP_FRAME_WIDTH),
                        self.scale * self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print("Camera " + str(config["device"]) + " opened with:")
        print("  fourcc:            " + str(self.camera.get(cv2.CAP_PROP_FOURCC)))
        print("  width:             " + str(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)))
        print("  height:            " + str(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        print("  fps:               " + str(self.camera.get(cv2.CAP_PROP_FPS)))
        print("  buffersize:        " + str(self.camera.get(cv2.CAP_PROP_BUFFERSIZE)))
        print("  scale factor:      " + str(self.scale))
        print("  fx, fy, cx, cy:    " + str(self.intrinsics))
        print("")
        print("Sending delay:" + str(self.delay))

        if bool(config["capture_thread"]):
            print("Using async capture thread.")
            self.capture_thread = Thread(target = self.run_capture, args=(self,))
            self.running = True
            self.capture_thread.start()
        
        
    def process(self, data, image, receiver_channel):

        if not self.running:
            # Make sure to continuously grab frames even if we don't deliver them.
            # # this avoids outdated images in the driver's queue.
            self.capture_image()

        if (not self.new_image.isSet()) or ((get_time_ms() - self.last_send) < self.delay):
            return None, None
            
        self.lock.acquire()
        timestamp = self.timestamp
        image = self.image
        self.timestamp = None
        self.image = None
        self.new_image.clear()
        self.lock.release()

        data = {'timestamp': timestamp}
        data['image_shape'] = image.shape
        data['camera'] = self.intrinsics

        self.last_send = get_time_ms()

        return data, image

    @staticmethod
    def run_capture(self):
        while (self.running):
            self.capture_image()
            time.sleep(0.001)

    def capture_image(self):
        start_time = get_time_ms()
        ret, im = self.camera.read()
        end_time = get_time_ms()

        if not ret:
            return

        if USE_SELF_ESTIMATED_TIMESTAMP:
            timestamp = (start_time + end_time) / 2
        else:
            # This call requires V4L2 API
            timestamp = self.camera.get(cv2.CAP_PROP_POS_MSEC)

        im = cv2.resize(im,(0,0), fx = self.scale, fy = self.scale)
        self.lock.acquire()
        self.timestamp = timestamp
        self.image = im
        self.new_image.set()
        self.lock.release()


    def guessIntrinsics(frame_width, frame_height):
        cx = frame_width / 2.0
        cy = frame_height / 2.0
        fx = 500.0 * (frame_width / 640.0)
        fy = 500.0 * (frame_height / 480.0)

        fx = (fx + fy) / 2.0
        fy = fx

        return (fx, fy, cx, cy)

Module = ProcessBase(WebcamInput)
