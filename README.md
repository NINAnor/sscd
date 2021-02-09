# SSCD
 Salmon Scale Circuli Detector

### Installation prerequisites:
   - Conda
   - Git

### Tool installation

#### 1. Download SSCD code from github
```
> git clone https://github.com/bcaneco/SSCD.git
```


#### 2. Set-up Conda environment for SSCD
```
> conda env create -f condaenv_sscd.yml

> conda activate ssdc
```

#### 3. Add <envname> environment to jupyter notebook
```
python -m ipykernel install --user --name sscd --display-name "SSCD"
```


#### 4. Download Yolov3 weights for focus and circuli detectors
Probably use dropbox?


### how to update conda environment
```
conda env update --name sscd --file condaenv_sscd.yml  --prune

```


### Download Yolo weights for focus and circuli detectors
  - Download the folder https://www.dropbox.com/sh/xm2zmoz7h9g5nqi/AACfwx7_JQmUkcNK8ePXetkta?dl=0


## Usage constraints
 - scale orientation
 - original image resolutions
 - Magnification
 - One scale per image only


## References (supporting code)
