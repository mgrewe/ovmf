# The Open Virtual Mirror Framework (OVMF)


The Open Virtual Mirror Framework (OVMF) is an open source toolbox for virtual mirror experiments in enfacement research and beyond.
The OVMF can track a large range of facial movements, including pose and expressions, and transfer them to realistic avatar faces.
It has been designed to run on standard computer hardware and easily interfaces with existing toolboxes for psychological experimentation, while satisfying the requirement of a tightly controlled experimental setup.
Further, it is designed to enable convenient extension of its core functionality such that it can be flexibly adjusted to many experimental paradigms.

![Example experiment created with the Open Virtual Mirror Framework](./data/framework.jpg)

Please refer to our BRM paper for more details and cite it if you are using our work:

> C.M. Grewe, T. Liu, A. Hildebrandt, S. Zachow: The Open Virtual Mirror Framework for enfacement illusions. Enhancing the sense of agency with avatars that imitate facial expressions. In: Behavior Research Methods (2022) https://doi.org/10.3758/s13428-021-01761-9



# Get Started

## Conda Environment

## Download Avatars

## Installation

# Webcam Setup

A good configuration of the webcam is of great importance. 
The camera's parameters significantly effect the end-to-end latency and the tracking performance. 
For a well-working setup, it might be necessary to tune the parameters of the specific hardware and lab environment.

Most webcams, like the Logitech Brio used in our experiments, allow the user to control various parameters. 
However, the number of parameters and the interpretation of the values vary between models and vendors. 
Please refer to the documentation of your webcam for more details.

## Exposure Time

One major parameter is the camera's exposure time, i.e., the time that is needed to capture an image. 
The smaller it is, the lower the latency becomes.

`v4l2-ctl` allows adjustment of the exposure in Linux, e.g., via

    v4l2-ctl -d /dev/video0 -c auto_exposure=1 
    v4l2-ctl -d /dev/video0 -c exposure_time_absolute=25

## Brightness and Contrast

Adjustment of the exposure time also affects the brightness and the signal-to-noise ratio of the images.
Short exposure times make the image appear darker.
Most cameras allow to increase the gain (similar to the ISO setting of DSLRs), but the resulting images might be too noisy.
You need to find a good compromise between exposure time and image quality.

Under Linux, you can try to play with gain, brightness, contrast, or other parameters, e.g.,

    v4l2-ctl -d /dev/video0 -c gain=150
    v4l2-ctl -d /dev/video0 -c brightness=200 
    v4l2-ctl -d /dev/video0 -c contrast=128


## Autofocus

Many cameras have an autofocus function. 
It continuously adjusts the focus to maintain sharpness as the distance of the face to the camera changes. 
In a lab setting, participants usually have a constant distance to the camera which allows to disable the feature. 
This may reduce latency and avoid tracking problems when the re-focussing procedure causes blurry images.

The focus and zoom can be set by

    v4l2-ctl -d /dev/video0 -c focus_automatic_continuous=0
    v4l2-ctl -d /dev/video0 -c focus_absolute=50 
    v4l2-ctl -d /dev/video0 -c zoom_absolute=100
    

## Other parameters

Other parameters of webcams include automatic white balance, backlight compensation, etc.

You can get a full list of the parameters using

    v4l2-ctl -d /dev/video0 --all


# Latency Calibration

The end-to-end latency of the OVMF can be calibrated using the automatic procedure described [here](./latency_calibration/README.md).

# Usage

# Extension

Example module for expression amplification/attenuation


# Pipelines

