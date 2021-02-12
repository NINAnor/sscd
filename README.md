# SSCD
 Salmon Scale Circuli Detector (SSCD)

## Prerequisites

In order to install and use SSCD the following programmes need to be installed:
   - Conda (its lighter version [Miniconda][1] is recommended)
   - [Git][2]

[1]: https://docs.conda.io/en/latest/miniconda.html{:target="_blank"} "Miniconda Installers"
[2]: https://git-scm.com/downloads{:target="_blank"} "Git Installers"

## Installation
<!-- Please take the following steps to install  -->

### 1. Download/clone SSCD code from GitHub
Two options:

  - Download the a zip file with the SSCD code

    1. Go to https://github.com/bcaneco/SSCD
    2. Hit the green dropdown button "Code" and select "Download ZIP"
    3. Extract `SSCD-main.zip` to a directory of your choice
    4. Rename the folder `SSCD-main` as `SSCD`


  - Clone the GitHub repository

    1. Open the command prompt
    2. Go to a directory of your choice (which will comprise SSCD's code)
    3. Clone the SSCD repository by typing the following
    ```
    > git clone https://github.com/bcaneco/SSCD.git
    ```


### 2. Set-up Conda environment for SSCD
This step creates a Conda environment for SSCD tool, with all the required packages and python dependencies being automatically installed.

  - Open a conda prompt (**Start** > **Anaconda** > **Anaconda Prompt**)
  - Navigate to the SSCD directory
  - Create SSCD environment:
      ```
      > conda env create -f condaenv_sscd.yml
      ```

  - Activate the environment:
    ```
    > conda activate sscd
    ```

  - Add SSCD conda environment to Jupyter notebook
    ```
    > python -m ipykernel install --user --name sscd --display-name "SSCD"
    ```


### 3. Download YOLOv3 weights for focus and circuli detectors

  - Download the file `yoloV3_checkpoints.zip`, containing the yolo weights for the two detectors (790MB total size), from this [link][3]

  - Unzip `yoloV3_checkpoints.zip` **inside the subdirectory `SSCD/data/`**

[3]: https://www.dropbox.com/sh/xm2zmoz7h9g5nqi/AACfwx7_JQmUkcNK8ePXetkta?dl=0


## How to run SSCD for detection

1. Open a conda prompt (**Start** > **Anaconda** > **Anaconda Prompt**)

2. Go to the SSCD directory

3. Activate the SSCD environment:

  ```
  > conda activate sscd
  ```

4. Two alternatives to run SSCD:

    4.1. Via a Jupyter Notebook (**recommended**)

    - Launch Jupyter lab:

      ```
      > jupyter lab
      ```

    - On Jupyter's File Browser, open `SSCD/docs/SSCD detection example usage.ipynb` and follow the instructions

    - **Alternatively**, open a new Notebook with `SSCD` as its Kernel, copy-paste the following chuck of code to a cell

    ```
    %run sscd.py \
       --img_dir "./data/example_scales"\
       --output_dir "C:/SSCD_temp_outputs"\
       --transect_angles 0 45 90 135 180 \
       --plot_detections True
    ```
    and hit `Ctrl+Enter` to run.

    4.2. Via the command prompt (more messy because of Tensorflow's verbose logging messages)

    Run the following chuck of code directly into the command line

   ```
   > python sscd.py ^
      --img_dir "./data/example_scales" ^
      --output_dir "C:/SSCD_temp_outputs" ^
      --transect_angles 0 45 90 135 180  ^
      --plot_detections True
   ```



### `sscd.py` Arguments

| Argument            | Description                                                                       | Type          | Default         |
|---------------------|-----------------------------------------------------------------------------------|---------------|-----------------|
| `--img_dir`         | Directory path containing scale image files. <br> Expects .tif images             | str           |                 |
| `--output_dir`      | Directory path where outputs will be stored                                       | str           |                 |
| `--transect_angles` | Choice of angle(s) for radial transects relative to focus <br> in degrees (0-360) | int (spaced)  | 0 45 90 135 180 |
| `--plot_detections` | Generate images with detections?                                                  | bool          | True            |



### Outputs structure

The following directory tree represents how the outputs from SSCD are structured:

<!-- Tree obtained via "tree /F" in command line -->

```
<output_dir>
   ├─── detections
   │   ├─── circuli
   │   │     │   ├─── circuli_spacings.csv
   │   │     │   └─── detections.csv
   │   │     │
   │   │     └─── detection_images
   │   │           ├─── N Esk NC_2018_273_0_detections.jpg
   │   │           ├─── N Esk NC_2018_273_180_detections.jpg
   │   │           ├─── N Esk NC_2018_273_225_detections.jpg
   │   │           ├─── N Esk NC_2018_273_270_detections.jpg
   │   │           ├─── N Esk NC_2018_273_315_detections.jpg
   │   │           ├─── N Esk NC_2018_273_90_detections.jpg
   |   |           ...
   │   │
   │   └─── focus
   │         │  └─── detections.csv
   │         │
   │         ├─── detection_images
   │         │      ├─── N Esk NC_2018_273_detections.jpg
   │         │      ├─── N Esk NC_2018_354_detections.jpg
   │         │      ...
   │         │
   │         └─── imgs_with_no_detections
   │               ├─── N Esk NC_2018_303.jpeg
   │               ...
   │
   └─── jpegs
         ├─── scales
         │      ├─── N Esk NC_2018_273.jpg
         │      ├─── N Esk NC_2018_303.jpg
         │      ...
         │
         └─── transects
              ├─── N Esk NC_2018_273_0.jpg
              ├─── N Esk NC_2018_273_180.jpg
              ├─── N Esk NC_2018_273_225.jpg
              ├─── N Esk NC_2018_273_270.jpg
              ├─── N Esk NC_2018_273_315.jpg
              ├─── N Esk NC_2018_273_90.jpg
              ...
```


- The `/jpegs` folder comprises images generated during the process, i.e. the JPEG versions of the original TIF scale images and the transect images
- The `/detections` folder comprises the detection data from each detector (e.g. `/detections/focus/detections.csv`), the circuli spacings (`detections/circuli/circuli_spacings.csv`), and subdirectories containing the images with drawn detection boxes if `--plot_detections` is set to `True` (e.g. `/detections/focus/detection_images`)
- In addition, images where detectors fail to locate the scale focus, or any circuli bands in a transect, are copied to a dedicated directory (e.g. `output_dir/detections/focus/imgs_with_no_detections`)




<!--
### how to update conda environment
```
conda env update --name sscd --file condaenv_sscd.yml  --prune

``` -->


<!-- ### Usage constraints
 - scale orientation
 - original image resolutions
 - Magnification
 - One scale per image  -->


### References (supporting code)
- [YOLOv3 implementation in Tensorflow 2](https://github.com/zzh8829/yolov3-tf2)
- [Diagonal crop](https://github.com/jobevers/diagonal-crop)
