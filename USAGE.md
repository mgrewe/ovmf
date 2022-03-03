# Usage

You can run the example pipeline of the OVMF by running the following command in the conda environment from the OVMF root directory, e.g., `C:\Users\mgrewe\ovmf`.

    python start.py -p example

This launches the OVMF modules in the example pipeline, including a preview window showing the tracked landmarks, a Blender window, and a PsychpPy window. 
During an experiment, you can simply minimize the Blender window.
Note that the size of the 3D view in the Blender window determines the resolution of the rendered image.
Rendering of larger images will increase the latency (see also [latency calibration](INSTALLATION.md#4-latency-calibration)).

The pipeline can be ended by hitting `q + Enter` in the console window.

## Logfiles

The output of the modules is written to log files that are located in the [logs](./logs) directory.
The output of the modules can also be toggled by hitting `n + Enter` in the console window.

## Pipelines

The OVMF has a modular design, i.e., its functionality is implemented across multiple modules which can be flexibly combined.
We call such a combination of modules a *pipeline*.
Each pipeline specifies how messages are passed between modules.

![OVMF pipeline](data/pipeline_example.jpg)

A message contains an image and additional data associated to it, e.g., the parameters of the tracked movements.
Messages are passed form the initial to the last module in feed-forward fashion.

The modules operate in parallel so that different messages can be processed simultaneously. 
For instance, face tracking can be performed for a new webcam image while a previous frame is still being processed for the animation and rendering of the avatar.

## Pipeline Configuration

A pipeline is configured in a JSON file located in `config/pipelines`.
The file has a simple format:

```json
{
	"webcam_input": {
	},
	"openface_tracker": {
        "send_image": false,
		"receive":{
            "image_data": "webcam_input"
		}
	},
    "image_preview": {
        "receive":{
            "image_data": "webcam_input",
            "tracker_parameters": "openface_tracker"
        }
    },
	"delay": {
		"receive":{
			"tracker_parameters": "openface_tracker"
		}
	},
	"openface_to_fexmm_remapper": {
		"receive" : {
			"tracker_parameters": "delay"
		}
	},
	"blender_renderer": {
		"blend": "data/fexmm_avg_face.blend",
		"init": "modules/blender_renderer/blender_avatar.py",
		"receive": {
			"fexmm_parameters": "openface_to_fexmm_remapper"
		}
	}
}
```

This pipeline contains the 6 modules of a simple virtual mirror experiment, i.e., (1) webcam capture, (2) face tracking, (3) image preview, (4) delay, (5) parameter remapping, (6) rendering.
The first value determines the type of module, e.g., `webcam_input`.

### Module Channels

Each module receives data from previous modules through channels as specified in the `receive` array. 
A module can have multiple receiver channels as in the `image_preview`.
Each channel has a name, e.g., `image_data`, and the name of the previous module, e.g., `webcam_input`.

### Module Parameters

The modules can be configured with additional parameters.
For instance, `send_image` specifies whether the webcam image is forwarded to subsequent modules. 
Setting this parameter to `false` saves time and reduces latency, but later modules will only receive a `None` image.
In the example above, modules after `openface_tracker` only process the tracked parameters such that the image can be safely discarded.

### System-wide and Pipeline-specific Parameters

An overview about the modules and parameters is given in [`config/modules.json`](config/modules.json).
Note that the parameters in this file are specified system-wide.
This is typically fine for the webcam device, but different pipelines may require different parameters.
The system-wide parameters can thus be overridden for each pipeline in the corresponding JSON file (e.g., `send_image` option in the example above.)

## PsychoPy Experiment

For convenience, the OVMF provides a [Python interface](modules/external/ovmf.py). 
It can be used from many toolboxes for psychological experimentation such as PsychoPy or OpenSesame.
Here is an example code of how OVMF can be integrated into a PsychoPy experiment.


```python
from psychopy import visual, core
import ovmf

# Create the virtual mirror interface
vm_interface = ovmf.Interface()
# Set 5 seconds delay
vm_interface.set_delay(0)

# Create PsychoPy window and image stimulus
win = visual.Window(
    size=[1088, 728],
    units="pix",
    fullscr=False,
    gammaErrorPolicy = 'ignore',
    waitBlanking=False)
img = visual.ImageStim(win, units = 'pix')
img.size = [640, 480]
img.setAutoDraw(True)

# Run forever
while True:
    # Receive and set image
    vm_interface.receive_and_set_image(img)
    win.flip()
```

PsychoPy can be started as a module directly by the OVMF (see [modules/external/psychopy_example.py](modules/external/psychopy_example.py)).
Alternatively, the OVMF can also be started in the background while a separate PsychoPy session is used for every participant (see [modules/external/psychopy_example_standalone.py](modules/external/psychopy_example_standalone.py)).

## Creation of New Modules

Our goal was to make the extension of the OVMF as convenient as possible.
As explained in our paper, most basic functionality of the OVMF, including message passing etc., is encapsulated into a base class called [`ModuleBase`](lib/module_base.py), such that it can be hidden from the user.
I.e., a module for the scaling of the tracked expression movements is as simple as

```python
from lib.module_base import ModuleBase, ProcessBase

class ExpressionScaling(ModuleBase):

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self.au_scale = config['expressionscaling_au_scale']


    def process(self, data, image, receiver_channel):
        if 'au' in data.keys():
            for key, value in data['au'].items():
                data['au'][key] = self.au_scale * value
        return data, image


    def process_control_commands(self, update, receiver_channel):
        if 'expressionscaling_au_scale' in update:
            self.au_scale = float(update['expressionscaling_au_scale'])
        

Module = ProcessBase(ExpressionScaling)
```

New functionality can be simply implemented by overriding of the `process` method.
The example shows how the values in the data dictionary are scaled by the factor names `au_scale`.
It can be set once at creation of the module via the system-wide or pipeline parameters (e.g., via specification in `modules.json` or `example.json`).

### Runtime Configuration of Modules

Alternatively, OVMF also supports runtime configuration of modules through the [interface](./modules/external/ovmf.py) from external Python applications.
For instance, a user might want to change the expression scale between two trials within a PsychoPy experiment, similar of `set_delay` function in the [PsychoPy example](#psychopy-experiment).
This can be achieved by overriding of the `process_control_commands` that receives all parameters in the `update` dictionary that were set via the generic `ovmf.Interface().set_parameter` function (see also [ovmf.py](modules/external/ovmf.py)).

A template module can be found in [modules/template/mymodule.py](modules/template/mymodule.py).
