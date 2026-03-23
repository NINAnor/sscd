# SSCD
 Salmon Scale Circuli Detector (SSCD)



 __Table of Contents__

   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [How to run SSCD](#how-to-run-sscd)
   - [Evaluating SSCD's performance](#evaluating-sscds-performance)
   - [SSCD Training](#sscd-training)


## Prerequisites

In order to install and use SSCD the following programmes are required to be installed:
  - [uv](https://docs.astral.sh/uv/getting-started/installation/)
  - [Git][2]


## Installation

#### 1. Clone the SSCD code repository

```bash
git clone <repository-url>
cd sscd
```

#### 2. Set-up the project environment

This step creates a virtual environment for the SSCD tool, with all the required packages and Python dependencies being automatically installed.

```bash
uv sync --dev
```

##### Register the Jupyter kernel

Add the SSCD environment to Jupyter notebook:
```bash
uv run ipython kernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=sscd
```
This registers this project environment as a kernel `sscd`, which is an isolated environment you can use to run your code.
If the kernel is not available in the list of kernels, refresh the page and it should appear.


#### 3. Download YOLOv3 weights for focus and circuli detectors

  Run the following command to download and extract the trained weights (~790 MB) into `data/yoloV3_checkpoints/`:

  ```bash
  uv run sscd-fetch weights
  ```

  That's it: installation (hopefully) done!


#### 4. Updating the SSCD Environment

The SSCD's environment should be updated if project dependencies change (e.g. in `pyproject.toml`).
Once the most recent version has been pulled to the local repository, update the SSCD environment with:
```bash
uv sync --dev
```

#### 5. How to install a package
Run `uv add <package-name>` to install a package. For example:
```bash
uv add requests
```

## How to run SSCD

Two alternatives to run SSCD:

### Via a Jupyter Notebook (**recommended**)

  - Launch Jupyter lab:

    ```bash
    uv run --with jupyter jupyter lab
    ```

  - On Jupyter's File Browser, open `SSCD/docs/SSCD detection example usage.ipynb` and follow the instructions
  - **Alternatively**, open a new Notebook with `sscd` as its Kernel, copy-paste the following code to a cell
    ```
    %run sscd.py \
       --img_dir "./data/example_scales"\
       --output_dir "./SSCD_temp_outputs"\
       --transect_angles 0 45 90 135 180 \
       --plot_dets True
    ```
    and hit `Ctrl+Enter` to run.

### Via the command line

  Run the following:

  ```bash
  uv run python sscd.py \
    --img_dir "./data/example_scales" \
    --output_dir "./SSCD_temp_outputs" \
    --transect_angles 0 45 90 135 180  \
    --plot_dets True
  ```


### `sscd.py` inputs

| Argument               | Description                     | Type          | Default         |
|------------------------|---------------------------------|---------------|-----------------|
| `--img_dir`    | Directory path containing scale image files. Expects TIF images  | str  |      |
| `--output_dir` | Directory path where outputs will be stored                      | str  |      |
| `--transect_angles` | Choice of angle(s) for radial transects in degrees (0-360)  | int (spaced) | `0 45 90 135 180` |
| `--plot_dets`    | Option to generate images with detections, for visual inspection   | bool   | `True` |
| `--transect_max_boxes` | Maximum number of detections per transect image              | int    | `200`  |


### `sscd.py` outputs

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
   ├─── jpegs
   |     ├─── scales
   |     │      ├─── N Esk NC_2018_273.jpg
   |     │      ├─── N Esk NC_2018_303.jpg
   |     │      ...
   |     │
   |     └─── transects
   |          ├─── N Esk NC_2018_273_0.jpg
   |          ├─── N Esk NC_2018_273_180.jpg
   |          ├─── N Esk NC_2018_273_225.jpg
   |          ├─── N Esk NC_2018_273_270.jpg
   |          ├─── N Esk NC_2018_273_315.jpg
   |          ├─── N Esk NC_2018_273_90.jpg
   |          ...
   |
   └─── log_sscd_detection.log
```


- The `/jpegs` folder comprises images generated during the process, i.e. the JPEG versions of the original TIF scale drwn images and the transect images
- The `/detections` folder comprises the detection data from each detector (e.g. `/detections/focus/detections.csv`), the circuli spacings (`detections/circuli/circuli_spacings.csv`), and subdirectories containing images with detection boxes drawn in them if `--plot_dets` is set to `True` (e.g. `/detections/focus/detection_images`)
- `log_sscd_detection.log` contains logging messages generated during the detection process, providing useful info from each step of the detection pipeline
- In addition, images where detectors fail to locate the scale focus, or any circuli bands in a transect, are copied to a dedicated directory (e.g. `output_dir/detections/focus/imgs_with_no_detections`)


## Evaluating SSCD's performance

Evaluating the performance of the SCCD is crucial to identify degradation in the system's capacity to produce reliable detections of circuli bands, and subsequently provide accurate intercirculi spacings. Consistent drops in evaluation metrics on new images, compared to [those][5] obtained when the system was last trained, indicates the system needs to be [retrained](#sscd-training) with fresh images.

The performance of each detector comprised in SSCD's pipeline can be evaluated via the `eval_detector.py` function. This tool combines outputs from the `sscd.py` script with annotation data (provided by the user) to produce standard object detection evaluation metrics.

Core computational tasks were adapted from [this project][4], where background information on evaluation methods for object detection algorithms and relevant performance metrics can also be found.

A more detailed guide for evaluating the performance of SSCD's detectors is available [here][6].

The following code chunk exemplifies the evaluation of the circulus detector in a jupyter session (under the sscd kernel):
```
%run eval_detector.py \
    --img_dir "./data/eval_example/imgs/" \
    --anns_dir "./data/eval_example/anns/" \
    --dets_csv "./data/eval_example/detections.csv"\
    --iou_threshould 0.5 \
    --output_dir "./SSCD_temp_outputs"\
    --plot_dets_vs_anns True \
    --sep_plots True
```

Running the same case usage via the command line:

```bash
uv run python eval_detector.py \
    --img_dir "./data/eval_example/imgs/" \
    --anns_dir "./data/eval_example/anns/" \
    --dets_csv "./data/eval_example/detections.csv" \
    --iou_threshould 0.5 \
    --output_dir "./SSCD_temp_outputs" \
    --plot_dets_vs_anns True \
    --sep_plots True
```

### `eval_detector.py` inputs


| Argument     | Description                                             | Type          | Default  |
|--------------|---------------------------------------------------------|---------------|----------|
| `--img_dir`  | Directory path to images for evaluation. Expects JPEG images | str    |          |
| `--anns_dir` | Directory path to annotation files. Expects XML files with Pascal VOC format  | str  |       |
| `--dets_csv` | Filepath to CSV file containing detection bounding boxes, as outputted from `sscd.py`| str | |
| `--iou_threshould` | IOU threshold (IOU<sub>thresh</sub>) determining if a detection is TP or FP (see "Metrics" section bellow) | float  | `0.5`  |
| `--output_dir`| Directory path to evaluation outputs | str           |          |
| `--plot_dets_vs_anns` | Option to generate image plots contrasting detections with annotations | bool   | `True` |
| `--sep_plots` | Option to produce separate plots for detections and annotations. If `False` draw both in the same plot (recommended for focus detections) | bool  | `False`  |


### `eval_detector.py` outputs

Evaluation metrics are printed to the active console, and stored with other relevant outputs as follows (for the above example case):

```
<output_dir>
    ├─── dets_vs_anns_plots
    |        ├─── N Esk NC_2018_186_0_dets_vs_anns.jpg
    |        ├─── N Esk NC_2018_186_180_dets_vs_anns.jpg
    |        ├─── N Esk NC_2018_186_90_dets_vs_anns.jpg
    |        ...
    |
    ├─── circulus_PRC.png
    ├─── evaluation_results.txt
    ├─── log_sscd_evaluation.log
    └─── results_by_image.csv
```

where:

  - `circulus_PRC.png` - Precision-Recall curve for the object class under evaluation
  - `evaluation_results.txt` - Main evaluation metrics
  - `log_sscd_evaluation.log` - logging messages generated during the evaluation process
  - `results_by_image.csv` - Classification of detections by image
  - `/dets_vs_anns_plots` - contains detections vs. annotations image plots



#### Definitions and Metrics:
  - Intersection Over Union (IOU):  the overlapping area between the detection bounding box and the annotation bounding box divided by the area of union between them:

    ![](docs/images/iou.png)

  - IOU threshold (IOU<sub>thresh</sub>): determines if a detection is classified as True Positive or False Positive
  - True Positive (TP): a correct detection (i.e. a detection with IOU &ge; IOU<sub>thresh</sub>)
  - False Positive (FP): an incorrect detection (i.e. a detection with IOU &lt; IOU<sub>thresh</sub> **OR** an extra TP on the same annotation)
  - False Negative (FN): an undetected annotation
  - Precision: the proportion of correct positive detections = TP/(TP+FP)
  - Recall: the proportion of annotations correctly detected (*true positive rate*) = TP/(TP+FN)
  - Average precision (AP): a combination of precision and recall scores. Given by the area under the precision vs. recall curve (check [here][4] for more details).
  - F<sub>1</sub> score: the harmonic mean of precision and recall. Higher scores when both recall and precision are high.
  - Mean Centre Error (MCE): average of Euclidian distances (in pixels) between the centres of TP detection boxes and respective annotation boxes


> **Note of caution**
>
> Annotations are not ground truths in a strict sense. Target objects are marked manually and thence subject to human error and labelling ambiguity. Therefore, performance metrics are highly dependent not only on the accuracy of the detector, but also on the quality of annotations used on the evaluation. Image plots contrasting detections against annotations should help scrutinise if apparent drops in performance metrics are being driven by a deteriorating detector, by poor labelling, or both.

## SSCD Training

As mentioned above, retraining the SSCD's detectors might become necessary if/when performance levels on new set of scale images drop substantially from those observed after the latest training.

Each detector is a [YOLOv3][10] (*You Only Look Once*) model trained for its specific detection task. YOLOv3 models were implemented using [Tensorflow 2](https://www.tensorflow.org/) (an open-source deep learning library developed by Google), based on the excellent repository by [Zihao Zhang][7].

This [page][8] provides details on how to set up a workstation for (re)training the SSCD's detectors.

*[Training protocol][11] currently being written up.*


## Development

### Update from template
To update your project with the latest changes from the template, run:
```bash
uvx --with copier-template-extensions copier update --trust
```

You can keep your previous answers by using:
```bash
uvx --with copier-template-extensions copier update --trust --defaults
```

### (Optional) pre-commit
pre-commit is a set of tools that help you ensure code quality. It runs every time you make a commit.

First, install pre-commit:
```bash
uv tool install pre-commit
```

Then install pre-commit hooks:
```bash
pre-commit install
```

To run pre-commit on all files:
```bash
pre-commit run --all-files
```


### References (supporting code)
- [YOLOv3 implementation in Tensorflow 2][7]
- [Diagonal crop][9]
- Object detection evaluation [tool](https://github.com/rafaelpadilla/Object-Detection-Metrics#how-to-use-this-project)

[2]: https://git-scm.com/downloads "Git Installers"
[4]: https://github.com/rafaelpadilla/Object-Detection-Metrics
[5]: /docs/sscd_evaluate.md#evaluation-metrics-on-test-set-on-latest-training
[6]: /docs/sscd_evaluate.md
[7]: https://github.com/zzh8829/yolov3-tf2
[8]: /docs/sscd_setup_for_training.md
[9]: https://github.com/jobevers/diagonal-crop
[10]: https://arxiv.org/pdf/1804.02767.pdf
[11]: /docs/SSCD%20Training%20Protocol.ipynb
