# The Open Virtual Mirror Framework (OVMF)


The Open Virtual Mirror Framework (OVMF) is a toolbox for virtual mirror experiments developed by the [Computational Diagnosis and Therapy Planning Group](https://www.zib.de/visual/therapy-planning) at the Zuse Institute Berlin.
It is intended for psychological research on enfacement and beyond.
The OVMF can track a large range of facial movements, including head pose and facial expressions.
The tracked movements can be manipulated on-the-fly and used to animate realistic avatar faces.


![A virtual mirror experiment created with the OVMF](./data/framework.jpg)


Our goal is to make the usage of the OVMF as simple as possible:

- The OVMF can run on standard computer hardware with a low latency.
- It interfaces with existing software for psychological experimentation like PsychoPy.
- The OVMF can be easily extended for the implementation of a large range of experimental paradigms.
- It facilitates creation of a tightly controlled experimental setup.



The OVMF and third party software (e.g., [OpenFace](https://github.com/TadasBaltrusaitis/OpenFace/) and [Blender](https://www.blender.org/)) are open source.
This fosters sustainability, extensibility, and replicability in enfacement research.
A detailed description of the OVMF can be found in paper. Please cite it if you are using our work. 

> Grewe, C.M., Liu, T., Hildebrandt, A., & Zachow, S. *The Open Virtual Mirror Framework for enfacement illusions. Enhancing the sense of agency with avatars that imitate facial expressions.* Behavior Research Methods (2022) https://doi.org/10.3758/s13428-021-01761-9



The OVMF has been established by the project [EMOTIC](http://www.activeself.de/emotic-enfacement-manipulation-in-transmitted-inter-facial-communication/).
It will be further developed in the project [The Cognitive Control of Social Resonance](http://www.activeself.de/the-cognitive-control-of-social-resonance/).
Both projects are part of the Special Priority Programme [The Active Self](http://www.activeself.de/) which is funded by the German Research Foundation.

![SPP Active Self](data/spp_active_self_logo.jpg)


# Installation

We originally developed the OVMF for the Linux and Windows operating systems, but it should be possible to use it on Mac as well.
Please refer to the [installation instructions](./INSTALLATION.md).


# Usage

The OVMF is designed to 

![Demo](data/demo_tracking.gif)




pipeline launch

minimization of window

window size


## Pipelines

## Extension

Example module for expression amplification/attenuation

# OVMF Avatars

The avatars used in our evaluation study of the OVMF were created with our 3D Facial Expression Morphable (FexMM).
The FexMM may only be used for scientific purposes.
To obtain the avatars, please read and sign the [license agreement](data/fexmm_license_agreement.pdf) and send it to us.

![Avatar faces](./data/avatars.jpg)

More details on the FexMM can be found here:

> Grewe, C.M., Liu, T., Kahl, C.A., Hildebrandt, A., & Zachow, S. Statistical Learning of Facial Expressions Improves Realism of Animated Avatar Faces. Frontiers in Virtual Reality (2021) https://doi.org/10.3389/frvir.2021.619811