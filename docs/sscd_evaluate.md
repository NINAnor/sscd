# Evaluating SSCD's performance

This is a step-by-step guide to evaluate the performance of the Salmon Scale Circuli Detector (SSCD) on new, unseen to training, scale images. SSCD is composed by two object detection models, the **focus** and the **circuli** detectors, and  evaluation must therefore be carried separately for each detector.

This guide assumes detection has been already carried out and the goal is to assess performance on a sample of the images used in detection and contrast it with the performance at the time of the latest training.

The following table provides the expected performance metrics of each detector.


| Model            | Average Precision (AP)    | F1      | No of images    | Training date   |
|------------------|---------------------------|---------|-----------------|-----------------|
| Focus detector   | Directory path            |         |                 |                 |
| Circuli detector | Directory path            |         |                 |                 |


If consistently lower evaluation metrics are obtained for one of the detectors, retraining the deteriorating detector must be considered.

Performance evaluation is done by comparing detections with *ground truth* data, i.e. the *true* locations of the target features in each image. This is done by manually marking and labelling all features of interest present in a given image using an image annotation tool.

There are [many][1] image annotation tools available but, for its simplicity and ease of use, we recommend [LabelImg][2].

Please note, the evaluation tool described here expects annotation files to be in Pascal VOC format. So, if using a different annotation tool without the option of Pascal VOC as an output format, annotations will need to be converted accordingly (e.g. this [python package][3] offers a range of format conversions).

The next sections 



The evaluation process involves 2 main steps
  1. Select and label images
  2. Run evaluation


[1]: https://www.simonwenkel.com/2019/07/19/list-of-annotation-tools-for-machine-learning-research.html
[2]: https://github.com/tzutalin/labelImg#labelimg
[3]: https://github.com/monocongo/cvdata


## Step 1 - Select and label the images to use in evaluation

During the detection step, jpeg versions of the scales and transect images used in detection are stored in the subdirectory `<output_dir>\jpegs`.


From the set of images where detection was performed, copy the images to be used for evaluation to new folder.

For the focus detector, the target object is the focus in each sca

consists of contrasting the detections with "ground truth"
