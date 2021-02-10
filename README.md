# SSCD
 Salmon Scale Circuli Detector (SSCD)

## Prerequisites

In order to install and use SSCD the following programmes need to be installed:
   - Conda (its lighter version [Miniconda][1] is recommended)
   - [Git][2]

[1]: https://docs.conda.io/en/latest/miniconda.html "Miniconda Installers"
[2]: https://git-scm.com/downloads "Git Installers"

## Installation
<!-- Please take the following steps to install  -->

### 1. Download/clone SSCD code from GitHub
Two options available:

  - Download the a zip file with the SSCD code

    1. Go to https://github.com/bcaneco/SSCD
    2. Hit the green dropdown button "Code" and select "Download ZIP"
    3. Extract `SSCD-main.zip` to a directory of your choice (i.e. SSCD's parent directory)
    4. Rename the folder `SSCD-main` as `SSCD`


  - Clone the GitHub repository

    1. Open the command prompt
    2. Go to a directory of your choice (i.e. SSCD's parent directory)
    3. Clone the SSCD repository by typing the following
    ```
    > git clone https://github.com/bcaneco/SSCD.git
    ```


### 2. Set-up Conda environment for SSCD
This step creates a Conda environment for SSCD tool, with all the required packages and python dependencies being automatically installed.

  - Open a conda prompt (**Start** > **Anaconda** > **Anaconda Prompt**)
  - Enter the SSCD directory
  - Create SSCD environment by typing:
      ```
      > conda env create -f condaenv_sscd.yml
      ```

  - Activate the environment:
  ```
  > conda activate sscd
  ```

  - Add SSCD conda environment to Jupyter notebook
  ```
  python -m ipykernel install --user --name sscd --display-name "SSCD"
  ```


### 3. Download Yolov3 weights for focus and circuli detectors

  - Download the zip folder (790MB) from:
  - (to launch in a new window/tab) https://www.dropbox.com/sh/xm2zmoz7h9g5nqi/AACfwx7_JQmUkcNK8ePXetkta?dl=0
  - unzip "yoloV3_checkpoints.zip" to SSCD/data/



## How to run detection

<!--
### how to update conda environment
```
conda env update --name sscd --file condaenv_sscd.yml  --prune

``` -->


### Usage constraints
 - scale orientation
 - original image resolutions
 - Magnification
 - One scale per image only


### References (supporting code)
