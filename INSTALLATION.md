# Setup Environment

## Blender
Download [Blender](https://www.blender.org/download/), preferably portable version.

Install ZeroMQ into Blenders Python:
```
Blender/2.91/python/bin/python.exe -m pip install -U pip
Blender/2.91/python/bin/python.exe -m pip install pyzmq
```

## Compiler (Windows only)
Download and install [Visual Studio 2022 Build Tools](https://aka.ms/vs/17/release/vs_buildtools.exe). Select at least `MSVCv142 - VS 2019 C++ x64/x86 build tools` and `Windows 10 SDK` for installation.  
For more information check [this guide](https://wiki.python.org/moin/WindowsCompilers).

## Conda
Download and install [Miniconda 64-Bit](https://conda.io/miniconda.html) or full [Anaconda 64-Bit](https://www.anaconda.com/download/).  
For more information check [this guide](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).


# Setup and build OVMF

## OVMF
Clone/copy repo somehwere.  
In `config/contrib.json` adjust paths for Blender and OpenFace directories (see below).  
Open `Anaconda Powershell Prompt` or `Anaconda Prompt`.  
```
cd 'ovmf'
conda env create -f environment.yml
conda activate ovmf
```

## Openface
```
cd 'contrib/OpenFace'
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --config Release --parallel 8
```
[Downloading OpenFace models should be added to this guide!]

## EOS
```
cd 'contrib/eos'
python setup.py install
```


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
