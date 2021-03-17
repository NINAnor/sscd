# Evaluating SSCD's performance

### Overview

Here we provide a guide for evaluating the performance of the Salmon Scale Circuli Detector (SSCD) on new, unseen to training, images. SSCD is composed by two distinct object detection models, the **focus** and the **circulus** detectors, and evaluation must therefore be carried separately for each detector.

Performance evaluation is based on geometric-based comparisons between detections and *ground truth* data (also referred to as annotations). In the context of object detection, ground truths consist of (manually) marked bounding boxes delimiting target objects in images.

This guide assumes the detection step has been already carried out (using the [`sscd.py`](../README.md#how-to-run-sscd)  function), and the goal now is to assess the performance of one of the detectors on a set of images used in detection. Obtained evaluation metrics can then be contrasted with those observed when the detector was last trained. Considerable drops (>10%) in metrics provide a strong indication that the detector's expected prediction accuracy has declined, and therefore it should be retrained with fresh images.

The following table provides the evaluation metrics of each detector obtained on the test set at the time of the last training.

###### Evaluation metrics on test set
| Model            | Training date  | No. of images  | IOU<sub>Thresh</sub> | Average Precision (AP) | F<sub>1</sub>   |
|------------------|----------------|----------------|----------------------|------------------------|-----------------|
| Focus detector   | July 2020      | 103            |  0.5                 | 99.0%                  | 0.99            |
| Circulus detector| December 2020  | 81             |  0.5                 | 95.2%                  | 0.94            |

<br/><br/>
An important caveat of the evaluation process is the quality of the annotation data. Labelling, the process by which ground truths are generated, needs to be as accurate and consistent as possible Labelling circulus, in particular, may at times be challenging as identifying circuli bands can be ambiguous due to e.g. bands being too packed (specially on river growth), poor scale-to-slide imprinting or the occurrence of fissures/discontinuities in scale deposition. Poor quality annotation data will have a negative impact on performance metrics while the detector is still operating at expected levels of accuracy, potentially prompting the user to needlessly retrain the detector. Visual inspection of detections vs annotations plots should help to discern decay in the detector's performance from poor labelling.


<!--
An important caveat of the evaluation process is the quality of the annotation data:

  - Labelling, the process by which ground truths are generated, needs to be as accurate and consistent as possible.

  - Labelling circulus, in particular, may at times be challenging as identifying circuli bands can be ambiguous due to e.g. bands being too packed (specially on river growth), poor scale-to-slide imprinting or the occurrence of fissures/discontinuities in scale deposition.

  - Poor quality annotation data will have a negative impact on performance metrics while the detector is still operating at expected levels of accuracy, potentially prompting the user to needlessly retrain the detector.

  - Visual inspection of detections vs annotations plots should help to discern decay in the detector's performance from poor labelling. -->



### Additional software requirements

In order to perform evaluation, we need to provide the "ground truth"

Performance evaluation is done by comparing detections with *ground truth* data, i.e. the *true* locations of the target features in each image. This is done by manually marking and labelling objects of interest (i.e. the scale's focus or the circuli bands) present in a given image using an image annotation tool. There are [many][1] image annotation tools available but, for its simplicity and ease of use, we recommend [*LabelImg*][2].

Please note, the evaluation tool expects annotation files to be in Pascal VOC format. So, if using a different annotation software without Pascal VOC as an output format, annotations will need to be converted accordingly (e.g. this [python package][3] offers a range of format conversions).



## Evaluation Process

Here we assume you have installed *LabelImg* and have run `sscd.py` on a set of images.

<!-- The evaluation process involves 2 main steps
  1. Select and  images
  2. Run evaluation -->

#### 1. Select and label the images to use in evaluation

During the detection step, jpg versions of the scales and transect images used for detection are stored in the subdirectory `<output_dir>\jpegs`.


From the set of images where detection was performed, copy the images to be used for evaluation to new folder.

For the focus detector, the target object is the focus in each sca

#### 2. Set up files for evaluation

#### 3. Run evaluation


#### 4. Assess retraining



[this link](#overview)



[1]: https://www.simonwenkel.com/2019/07/19/list-of-annotation-tools-for-machine-learning-research.html
[2]: https://github.com/tzutalin/labelImg#labelimg
[3]: https://github.com/monocongo/cvdata
