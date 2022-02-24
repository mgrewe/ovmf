# 1. Setup Environment

## Blender
Download [Blender](https://www.blender.org/download/), we recommend to use the portable version.

### Windows
Install ZeroMQ into Python bundled with blender:

```
Blender/3.0/python/bin/python.exe -m pip install -U pip
Blender/3.0/python/bin/python.exe -m pip install pyzmq opencv-python
```

## Compiler (Windows only)
Download and install [Visual Studio 2019 Build Tools](https://aka.ms/vs/16/release/vs_buildtools.exe). Select `Desktop Development with C++` and then at least `MSVCv142 - VS 2019 C++ x64/x86 build tools` and `Windows 10 SDK` for installation.  
For more information check [this guide](https://wiki.python.org/moin/WindowsCompilers).

### Linux
Install the essential build tools including gcc, make, cmake.
E.g., for Ubuntu run

```
apt-get install build-essential
```


## Conda
Download and install [Miniconda 64-Bit](https://conda.io/miniconda.html) or full [Anaconda 64-Bit](https://www.anaconda.com/download/).  
For more information check [this guide](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).




# 2. Chekout OVMF and build OpenFace

## Create Conda environment
Create a conda environment for the ovmf

    conda create -n ovmf

Install git

    conda install git curl


    conda env update --file environment.yml


## Clone the repository
Open a terminal and navigate to the directory where the OVMF should be stored.

```
cd ~/projects/    # Change to a directory of your choice
git clone --recurse-submodules https://github.com/mgrewe/ovmf.git
cd ovmf

```

## Create Conda environment

Clone
Open `Anaconda Powershell Prompt` or `Anaconda Prompt`.  

```
conda env create -f environment.yml -n ovmf
conda activate ovmf
```

## Openface

Download pretrained detector models.

```
curl -L https://www.dropbox.com/s/7na5qsjzz8yfoer/cen_patches_0.25_of.dat -o contrib/OpenFace/lib/local/LandmarkDetector/model/patch_experts/cen_patches_0.25_of.dat

curl -L https://www.dropbox.com/s/7na5qsjzz8yfoer/cen_patches_0.35_of.dat -o contrib/OpenFace/lib/local/LandmarkDetector/model/patch_experts/cen_patches_0.35_of.dat

curl -L https://www.dropbox.com/s/7na5qsjzz8yfoer/cen_patches_0.50_of.dat -o contrib/OpenFace/lib/local/LandmarkDetector/model/patch_experts/cen_patches_0.50_of.dat

curl -L https://www.dropbox.com/s/7na5qsjzz8yfoer/cen_patches_1.00_of.dat -o contrib/OpenFace/lib/local/LandmarkDetector/model/patch_experts/cen_patches_1.00_of.dat

```

Build Openface.

```
cd 'contrib/OpenFace'
mkdir build 
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --config Release --parallel 8 --target FeatureExtractionPython
cd ../../..
```


# Configure OVMF

*TODO:* Correct

In `config/contrib.json` adjust paths for Blender and OpenFace directories (see below).  


# Download Avatar Model

# Run Pipeline
Open `Anaconda Powershell Prompt` or `Anaconda Prompt`.  
Activate environment:
```
conda activate ovmf
```
Run OVMF pipeline:
```
cd 'ovmf'
python start.py -p example
```
