# Compute latency

Method to compute the end-to-end latency of the OVMF. The single steps are described below.

1. A video of an avatar doing a head turn as [here](./head_turn.mp4) is prerecorded and continuously replayed.
2. It is captured by the webcam which is used by the OVMF, and the tracked movements are transferred to the avatar which is rendered to the screen.
3. Both avatars are displayed next to each other. Make sure that the webcam used by the OVMF only captures the prerecorded video, similar to this setup:

![latency_experiment_setup_example](./latency_experiment_setup_example.jpg)

4. A second camera is used to record both avatars, e.g., using an Android mobile phone with OpenCamera, available via the [Playstore](https://play.google.com/store/apps/details?id=net.sourceforge.opencamera&hl=de&gl=US) or [F-droid](https://f-droid.org/en/packages/net.sourceforge.opencamera/). Make sure to use a high frame rate.
5. Use the [OpenFace Toolkit](https://github.com/TadasBaltrusaitis/OpenFace/) to automatically track the poses of the two faces. 
    This can be done using the command line tool

                FaceLandmarkVidMulti -f <filename>.mp4
                
    It will generate a csv (normally in a subfolder called *processed*) which can be read by this script.
6. Adjust the [parameter section](##Parameters) below according to your setup and run the cells. Note that you also need to select the correct tracking ids of the faces from OpenFace.

The Jupyter notebook can be found [here](./end-to-end-latency.ipynb)