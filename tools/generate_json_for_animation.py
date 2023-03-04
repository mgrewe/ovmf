import sys
from pathlib import Path
ovmf_base_path = '/home/bzfgrewe/projects/ovmf/'
sys.path.append(str(Path(__file__).parents[1]))
from modules.input.video_input import VideoInput
from modules.openface.openface_tracker import OpenFaceTracker
from modules.openface.openface_remapper import OpenFaceRemapper
from modules.utils.smoothing import Smoothing
from modules.utils.image_preview import ImagePreview
from modules.utils.fade_in import FadeIn
from modules.utils.expression_scaling import ExpressionScaling
from modules.utils.json_disk_writer import JSONDiskWriter



# DOKUMENTATION
#
# Best to use videos with constant frame rate. Resampling can be achieved with ffmpeg:
#
# ffmpeg -i <input_video_file> -filter:v fps=30 -r 30 <output_video_file>
#
# Check framerate with
#
# ffprobe -v quiet -show_streams <input_video_file>  | grep avg_frame_rate


# Create config
config = {'use_sockets': False,
          'openface_tracker_parameters': '-wild -au_static',
          'video_filename': sys.argv[1],
          'json_filename': sys.argv[2],
          'smoothing_factor_au': 0.7,
          'smoothing_factor_pose': 0.7,
          'video_input_vflip': False,
          'video_input_hflip': True,
          'expressionscaling_au_scale': 1,
          # Decrease noise on sequence start, adjust to timing
          'fade_in_duration': 30
          }

modules = []
modules.append(
    VideoInput(config)
)
modules.append(
    ImagePreview(config)
)
modules.append(
    OpenFaceTracker(config)
)
modules.append(
    OpenFaceRemapper(config)
)
modules.append(
    FadeIn(config)
    )
modules.append(
    Smoothing(config)
    )
modules.append(
    ExpressionScaling(config)
    )
modules.append(
    JSONDiskWriter(config)
)

for i in range(modules[0].get_num_frames()):
    print('Processing frame:', i)
    data, image = None, None
    for m in modules:
        data, image = m.process(data, image, '')
    # print(data['au'])

for m in modules:
    m.finalize()

# reader = CSVDiskReader(au_file, None, config = config)
# smoother = Smoothing(config = config)
# smoother.dynamic_au_smoothing = False
# smoother.smoothing['au'] = 0.6
# smoother.smoothing['pose_rotation'] = 0.6
# smoother.smoothing['pose_location'] = 0.6
# remapper = FexMMRemapper(config = config)
