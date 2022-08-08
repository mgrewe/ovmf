from lib.module_base import ModuleBase, ProcessBase
import numpy as np
import pandas as pd
from auxiliary import get_time_ms

class OpenFaceDiskReader(ModuleBase):

    current_frame = 0
    images = None
    delay = None

    au_mapping = {
        'AU01_r': 'AU01', 
        'AU02_r': 'AU02',
        'AU04_r': 'AU04', 
        'AU05_r': 'AU05', 
        'AU06_r': 'AU06', 
        'AU07_r': 'AU07', 
        'AU09_r': 'AU09', 
        'AU10_r': 'AU10', 
        'AU12_r': 'AU12', 
        'AU14_r': 'AU14', 
        'AU15_r': 'AU15', 
        'AU17_r': 'AU17', 
        'AU20_r': 'AU20', 
        'AU23_r': 'AU23', 
        'AU25_r': 'AU25', 
        'AU26_r': 'AU26', 
        'AU45_r': 'AU45'
    }

    pose_names = ['pose_Tx' , 'pose_Ty', 'pose_Tz', 'pose_Rx', 'pose_Ry', 'pose_Rz']
    gaze_names = ['gaze_angle_x', 'gaze_angle_y']

    def __init__(self, filename, videopath = None, **kwargs):

        super().__init__(**kwargs)

        print("Reading " + filename)

        tmp = pd.read_csv(str(filename), skipinitialspace = True)

        self.au_data = np.array(tmp[self.au_mapping.keys()])
        self.pose_data = np.array(tmp[self.pose_names])
        self.gaze_data = np.array(tmp[self.gaze_names])

        print("Parsed " + str(self.get_num_frames()) + " lines.")

        # if image_path:
        #     import cv2
        #     import glob
        #     self.images = []
        #     #image_path = pl.Path(image_path)
        #     print(image_path)
        #     imfiles = sorted(glob.glob(image_path))
        #     for imfilename in imfiles:
        #         # imfilename = image_path / "frame_det_00_{:06d}.bmp".format(i+1)
        #         self.images.append(cv2.imread(str(imfilename)))

        if videopath:
            import cv2
            self.images = []
            vid = cv2.VideoCapture(videopath)
            while True:
                ret, image = vid.read()
                if not ret:
                    break
                self.images.append(image)
            print('Read video with ' + str(len(self.images)) + " frames.")

    def get_num_frames(self):
        return self.pose_data.shape[0]
    
    def process(self, data, image, receiver_channel):

        true_frame = self.current_frame % self.get_num_frames()

        data = {}
        pose = self.pose_data[true_frame,:]
        aus = self.au_data[true_frame,:]
        gaze = self.gaze_data[true_frame,:]
        data['pose'] = pose.tolist()
        data['gaze'] = gaze.tolist()
        data['au'] = dict(zip(self.au_mapping.values(), aus.tolist()))
        data['timestamp'] = get_time_ms()

        if self.images:
            # import cv2
            # cv2.imshow('OpenFace', self.images[self.current_frame])
            # cv2.waitKey(25)
            image = self.images[true_frame]
        else:
            image = None

        self.current_frame += 1

        return data, image



Module = ProcessBase(OpenFaceDiskReader)



