import sys
import json
import pathlib as pl
import numpy as np

dir = str(pl.Path(__file__).resolve().parents[2])
if not dir in sys.path:
    sys.path.append(dir)
from lib.module_base import ModuleBase, ProcessBase


class OpenFaceTracker(ModuleBase):

    tracker = None

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

        with open(pl.Path(__file__).resolve().parents[2] / "config/contrib.json") as f:
            contrib_dict = json.load(f)
            openface_binary_dir = pl.Path(contrib_dict["openface_binary_dir"])
            if not openface_binary_dir.is_absolute():
                openface_binary_dir = pl.Path(__file__).resolve().parents[2] / openface_binary_dir
            openface_model_au_root_dir = pl.Path(contrib_dict["openface_model_au_root_dir"])
            if not openface_model_au_root_dir.is_absolute():
                openface_model_au_root_dir = pl.Path(__file__).resolve().parents[2] / openface_model_au_root_dir

        sys.path.append(str(openface_binary_dir))
        from openface import OpenFace
        self.tracker = OpenFace(str(openface_model_au_root_dir))


    def process(self, data, image, receiver_channel):

        if data is None or image is None:
            return None, None

        success = self.tracker.detect(image, data['camera'])

        if not success:
            return None, None


        data['pose'] = np.array(self.tracker.pose, dtype=float).tolist()
        data['au'] = dict(self.tracker.au)
        data['au_binary'] = dict(self.tracker.au_binary)
        data['landmark_data'] = np.array(self.tracker.landmark_data, dtype=float).tolist()
        data['landmark_visibility'] = np.array(self.tracker.landmark_visibility, dtype=float).tolist()

        return data, image


Module = ProcessBase(OpenFaceTracker)
