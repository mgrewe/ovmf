# Installation of the OVMF

We provide two ways of installing OVMF on your computer:

1. [Easy method](#easy-installation-for-windows): Step-by-step installation that uses a binary package created by us. This method works with Windows only. 

2. [Advanced method](#advanced-installation): Advanced installation including preparation of Blender and compilation of OpenFace. This works for Windows and Linux systems.


# 1. Easy Installation for Windows

Please follow the instructions step-by-step.
## 1.1 Install software libraries

If not installed on your system, please download and install the following packages.

- [Microsoft VC Runtime Libraries (16)](https://aka.ms/vs/16/release/vc_redist.x64.exe).
- [Miniconda 64-Bit](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe).
Alternatively, you can use full [Anaconda 64-Bit](https://www.anaconda.com/download/). 
For more information check [this guide](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).


## 1.2 Setup Conda environment

Open the `Anaconda Prompt` from the start menu. It will typically open in your user's home directory, e.g., `c:\Users\mgrewe`. You can change to a different directory or just install the OVMF there. 

To prepare and activate a conda environment, type the following lines into the `Anaconda Prompt`:

    conda create -n ovmf python=3.9
    conda activate ovmf
    conda install git git-lfs

## 1.3 Clone OVMF repository

Now, clone the git repository by execution of:

    git clone https://github.com/mgrewe/ovmf.git

## 1.4 Update Conda environment

Install required libraries with:

    cd ovmf
    conda env update -f .\environment.yml -n ovmf

## 1.5 Download Blender/OpenFace package

Download the [ZIP package](https://cloud.zib.de/s/tqTmrgP9LfDqSKG/download/Blender_OpenFace_Binary_Package_1.zip) and extract it into `ovmf\contrib`. 
It should now contain two directories, i.e., `Blender`  and `OpenFace`.

## 1.6 Start OVMF

Now, everything should be readily prepared such that you can start the OVMF via:

    python start.py -p example

The OVMF should start a Blender and a PsychoPy window showing an example scene like this

![Example Scene](data/CubeFace.jpg)

Learn how to obtain the FexMM avatars [here](README.md#download-avatar-model).

# 2. Advanced Installation

This walk-through installation will show you how to set up the OVMF with an original version of Blender and the source code of OpenFace.
This method has been tested on Windows and Linux.

## 2.1 Install compiler and build tools

We will now set up a working build tool chain for the compilation of OpenFace.

### Windows

Download and run [Visual Studio 2019 Build Tools](https://aka.ms/vs/16/release/vs_buildtools.exe). 
Select `Desktop Development with C++` and then at least `MSVCv142 - VS 2019 C++ x64/x86 build tools` and `Windows 10 SDK` for installation.
For more information check [this guide](https://wiki.python.org/moin/WindowsCompilers).

### Linux
Install the essential build tools. 
E.g., in Ubuntu simply run:

    sudo apt-get install build-essential


## 2.2 Install Conda

Download and install [Miniconda 64-Bit](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe).
Alternatively, you can use full [Anaconda 64-Bit](https://www.anaconda.com/download/). 
For more information check [this guide](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).


## 2.3 Setup Conda environment and clone OVMF repository

Create a Conda environment for the OVMF and activate it:

    conda create -n ovmf
    conda activate ovmf

If necessary, install git, git-lfs, and curl:

    conda install git git-lfs curl

Recursively clone the repository and its submodules:

    git clone --recurse-submodules https://github.com/mgrewe/ovmf.git
    cd ovmf

Install the required libraries in the conda environment. 
We also installed PsychoPy such that we can start the experiments directly with the OVMF. 
If it is not needed, you can remove the line from the `ovmf/environment.yml`.
Then run:

    conda env update -f environment.yml

## 2.4 Configure and Build OpenFace


Download pretrained detector models (In `Anaconda Powershell Prompt`, you need to write `curl.exe`):

    curl -L https://www.dropbox.com/s/7na5qsjzz8yfoer/cen_patches_0.25_of.dat -o contrib/OpenFace/lib/local/LandmarkDetector/model/patch_experts/cen_patches_0.25_of.dat

    curl -L https://www.dropbox.com/s/7na5qsjzz8yfoer/cen_patches_0.35_of.dat -o contrib/OpenFace/lib/local/LandmarkDetector/model/patch_experts/cen_patches_0.35_of.dat

    curl -L https://www.dropbox.com/s/7na5qsjzz8yfoer/cen_patches_0.50_of.dat -o contrib/OpenFace/lib/local/LandmarkDetector/model/patch_experts/cen_patches_0.50_of.dat

    curl -L https://www.dropbox.com/s/7na5qsjzz8yfoer/cen_patches_1.00_of.dat -o contrib/OpenFace/lib/local/LandmarkDetector/model/patch_experts/cen_patches_1.00_of.dat

Make sure do download the model files before the build such that they can be copied to the correct locations.
Then, configure and build Openface:

    cd contrib/OpenFace
    mkdir build 
    cd build
    cmake -DCMAKE_BUILD_TYPE=Release ..
    cmake --build . --config Release --parallel 4 --target FeatureExtractionPython
    cd ../../..


## 2.5 Install Blender
Download the portable version of [Blender](https://www.blender.org/download/).
Preferably, extract and move the files into the `ovmf/contrib/Blender` directory.

Blender comes with its own Python distribution. 
We need to manually install `pyzmq` for the communication with the OVMF.
This can be done by opening a terminal in the Blender directory and executing the following lines provided that the version is changed accordingly:

### Windows

    .\contrib\Blender/3.0\python\bin\python.exe -m pip install -U pip
    .\contrib\Blender/3.0\python\bin\python.exe -m pip install pyzmq


### Linux

    ./contrib/Blender/3.0/python/bin/python3.9 -m pip install -U pip
    ./contrib/Blender/3.0/python/bin/python3.9 -m pip install pyzmq


## 2.6 Configure OVMF

OVMF needs to know the location of Blender and OpenFace. 
Adjust the paths in `ovmf/config/contrib.json` accordingly.
Below the OVMF directory, relative paths can be used, e.g.,

    {
        "blender_executable": "contrib/Blender/blender",
        "openface_binary_dir": "contrib/OpenFace/build/bin/",
        "openface_model_au_root_dir": "contrib/OpenFace/build/bin/"
    }


## 2.7 Start OVMF

Now, everything should be setup. Run the example as described [here](#6-start-ovmf).


