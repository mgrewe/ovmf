# Webcam Setup

The configuration of the webcam is of great importance. 
The camera's parameters significantly effect the end-to-end latency and the tracking performance. 
For a well-working setup, it might be necessary to tune the parameters of the specific hardware and lab environment.
For best results, light the lab as brightly as possible.

Most webcams, like the Logitech Brio used in our experiments, allow the user to control various parameters. 
However, the number of parameters and the interpretation of the values may vary between vendors and models. 
Please refer to the documentation of your webcam for more details.

## Parameter Configuration

We provide the ability to set a number of parameters system-wide, or specifically for each pipeline in their respective JSON files (find for more information on the configuration of parameters [here](./USAGE.md#system-wide-and-pipeline-specific-parameters)).
Refer to [config/modules.json](config/modules.json) and [webcam_input.py](./modules/input/webcam_input.py) for all currently supported parameters.
The adjustment of each parameter by the OVMF can be deactivated with the special value `null`.
This way, the OVMF will not change the camera's parameter and the currently active configuration is used.
All other values will be set during starting of the `webcam_input` module.

**NOTE:** Once the parameters have been set, they will remain active also after the OVMF has been ended.
This might affect other software using the webcam, like Skype or Zoom.
It might thus be necessary to store the original parameters and reset them afterwards using the tool of your choice.
We are working on a solution to restore the parameters after the OVMF has been ended.

## Live Configuration

Windows and Linux provide tools which allow live tuning of the parameters during operation of the OVMF. 
For Windows, you can take advantage of a configuration dialog that will be shown during startup of the OVMF by setting `"win_props_dialog": true`.
For Linux, we will give examples for the usage of the command line tool `v4l2-ctl` below.
Please also refer to these tools for the valid ranges of the parameter values.

After live tuning, the optimal parameters can be written to [config/modules.json](config/modules.json) or the respective pipeline file.
This way, the correct parameters will be set during start of the `webcam_input` module.


## Exposure Time

One important parameter is the camera's exposure time, i.e., the time that the sensor will be exposed to the light coming through the lens of the camera.
The smaller it is, the faster an image is captured and the lower the latency becomes.
However, short exposure times will also make the image darker.

Usually, webcams try to automatically adjust exposure time to the amount of light in the image.
We recommend setting `"autoexposure": false` to deactivate dynamic adjustment and decrease latency.
Instead, try to brightly light the lab and decrease exposure time as much as possible.
With `v4l2-ctl`, you can set exposure mode to manual and adjust the absolute time via

    v4l2-ctl -d /dev/video0 -c auto_exposure=1 # deactivate auto exposure
    v4l2-ctl -d /dev/video0 -c exposure_time_absolute=25 # corresponds to 2.5 msec

You can also query the current parameters of a camera by

    v4l2-ctl -d /dev/video0 --all



**NOTE:** Windows and Linux parametrize exposure time differently.
The value of `"exposure"` in [config/modules.json](config/modules.json) is specified in milliseconds and correctly converted for each operating system.
If the value is determined using one of the tools for live tuning, a conversation of the tool's value according to the following formulas is necessary:
- Linux: value/10
- Windows: 1000/(2^(-1*value))

## Gain, Brightness, and Contrast

Adjustment of the exposure time also affects the brightness and the signal-to-noise ratio of the images.
Short exposure times make the image appear darker.
The gain can be increased which amplifies the image intensities similar to the ISO of a DSLR.
In consequence, the images become brighter but also more noisy.
You need to find a good compromise between exposure time and image quality.

Under Linux, you can try to play with gain, brightness, contrast, or other parameters, e.g.,

    v4l2-ctl -d /dev/video0 -c gain=150
    v4l2-ctl -d /dev/video0 -c brightness=200 
    v4l2-ctl -d /dev/video0 -c contrast=128


## Autofocus

Most cameras focus automatically, i.e., it is continuously adjusted to maintain sharpness of the face as the distance to the camera changes. 
In a lab setting, participants usually have a constant distance to the camera which allows to disable the feature via `"autofocus": false`.
This may reduce latency and avoid tracking problems when blurry images occur during re-focussing.

The focus and zoom can also be set by

    v4l2-ctl -d /dev/video0 -c focus_automatic_continuous=0
    v4l2-ctl -d /dev/video0 -c focus_absolute=50 
    v4l2-ctl -d /dev/video0 -c zoom_absolute=100
    

## Other parameters

Other parameters of webcams include automatic white balance, backlight compensation, etc.
You can get a full list of the parameters in Window's configuration dialog or in Linux using

    v4l2-ctl -d /dev/video0 --all

