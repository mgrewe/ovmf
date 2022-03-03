# Latency Calibration

We provide a method for calibrating the end-to-end latency of the OVMF.
The method is described in detail in our [paper](../README.md#the-open-virtual-mirror-framework-ovmf).
The Jupyter notebook can be found [Jupyter notebook](./end-to-end-latency.ipynb).

![latency_experiment_setup_example](./latency_experiment_setup_example.jpg)

The steps of the calibration procedure are:

1. A video of an avatar doing a head turn as [here](./head_turn.mp4) is prerecorded and continuously replayed.

2. The video is captured by the webcam which is used by the OVMF such that the tracked movements are transferred to a second avatar which is displayed on the screen, e.g., within PsychoPy.
An example calibration pipeline can be found [here](../config/pipelines/latency_calibration.json). 
It can be started with `python start.py -p latency_calibration`. 
You may use your own experimental pipeline.

3. Both avatars are displayed next to each other. Make sure that the webcam used by the OVMF only captures the prerecorded video, similar to the setup above.

4. A second camera is used to record both avatars, e.g., with an Android mobile phone with OpenCamera, available via the [Playstore](https://play.google.com/store/apps/details?id=net.sourceforge.opencamera&hl=de&gl=US) or [F-droid](https://f-droid.org/en/packages/net.sourceforge.opencamera/). Make sure to use a high frame rate.

5. Use the [OpenFace Toolkit](https://github.com/TadasBaltrusaitis/OpenFace/) to automatically track the poses of the two faces. 
    This can be done using the command line tool

                FaceLandmarkVidMulti -f <filename>.mp4
                
    It will generate a csv (normally in a subfolder called *processed*) which can be read by this script.

6. Adjust the path in the notebook's parameter section to point to the csv file and run the cells. 
Note that you may need to correct face ids which were assigned by OpenFace.
