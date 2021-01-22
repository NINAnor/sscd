# SSCD
 Salmon Scale Circuli Detector


### Installation

#### 1. Install prerequisites:
  - Conda
  - Git


#### 2. Download SSCD code from github
```
> git clone https://github.com/bcaneco/SSCD.git
```


#### 3. Set-up Conda environment for SSCD
```
> conda env create -f condaenv_sscd.yml

> conda activate ssdc
```

#### 4. Add <envname> environment to jupyter notebook
```
python -m ipykernel install --user --name sscd --display-name "SSCD"
```


#### 5. Download Yolov3 weights for focus and circuli detectors
Probably use dropbox?


### how to update conda environment
```
conda env update --name sscd --file condaenv_sscd.yml  --prune
```
