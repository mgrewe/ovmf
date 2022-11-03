from lib.module_base import ModuleBase, ProcessBase
import numpy as np
import pandas as pd
from auxiliary import get_time_ms


def find_nearest_index(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

class CSVDiskReader(ModuleBase):

    current_frame = 0
    images = None
    delay = None

    data = np.array([[]])

    au_names = [
        'AU01', 
        'AU02',
        'AU04', 
        'AU05', 
        'AU06', 
        'AU07', 
        'AU09', 
        'AU10', 
        'AU12', 
        'AU14', 
        'AU15', 
        'AU17', 
        'AU20', 
        'AU23', 
        'AU25', 
        'AU26', 
        'AU45'
    ]

    pose_names = [
        'translation_x' , 
        'translation_y', 
        'translation_z', 
        'rotation_x', 
        'rotation_y', 
        'rotation_z'
    ]

    gaze_names = [
        'gaze_angle_x', 
        'gaze_angle_y'
    ]

    def __init__(self, filename, videopath = None, **kwargs):

        super().__init__(**kwargs)

        print("Reading " + filename)

        self.data = pd.read_csv(str(filename), skipinitialspace = True)

        self.data_au_names = list(set(self.au_names).intersection(self.data.columns))
        self.data_pose_names = list(set(self.pose_names).intersection(self.data.columns))
        self.data_gaze_names = list(set(self.gaze_names).intersection(self.data.columns))

        if 'frame' not in self.data:
            print("NO FRAME FIELD FOUND")
            self.data['frame'] = list(range(self.data.shape[0]))


        self.data = self.data.set_index('frame')

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
        return self.data.shape[0]
    

    def process(self, data, image, receiver_channel):

        true_frame = self.current_frame % self.get_num_frames()

        data = {}

        if true_frame in self.data.index:
            dat = self.data.loc[true_frame]
        else:
            idx = find_nearest_index(self.data.index,true_frame)
            dat = self.data.iloc[idx]

        if self.pose_names:
            data['pose'] = dict([(v,0) for v in self.pose_names])
            data['pose'] = {**data['pose'], **dat[self.data_pose_names]}
            data['pose'] = list(data['pose'].values())
        if self.gaze_names:
            data['gaze'] = dict([(v,0) for v in self.gaze_names])
            data['gaze'] = {**data['gaze'], **dat[self.data_gaze_names]}
            data['gaze'] = list(data['gaze'].values())
        if self.au_names:
            data['au'] = dict([(v,0) for v in self.au_names])
            data['au'] = {**data['au'], **dat[self.data_au_names]}
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



Module = ProcessBase(CSVDiskReader)



