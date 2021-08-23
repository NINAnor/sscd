"""
Visualise a sample of instances (images and annotations) stored in a TFRecord dataset
"""

import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Parse TFRecords
def parse_image(example_proto):
    # Create a dictionary describing the features.
    image_feature_description = {
        'image/height': tf.io.FixedLenFeature([], tf.int64),
        'image/width': tf.io.FixedLenFeature([], tf.int64),
        'image/encoded': tf.io.FixedLenFeature([], tf.string),
        'image/filename': tf.io.FixedLenFeature([], tf.string),
        'image/object/class/label': tf.io.FixedLenSequenceFeature([], tf.int64, allow_missing=True),
        'image/object/difficult': tf.io.FixedLenSequenceFeature([], tf.int64, allow_missing=True),
        'image/object/bbox/ymax': tf.io.FixedLenSequenceFeature([], tf.float32, allow_missing=True),
        'image/object/bbox/xmax': tf.io.FixedLenSequenceFeature([], tf.float32, allow_missing=True),
        'image/object/bbox/ymin': tf.io.FixedLenSequenceFeature([], tf.float32, allow_missing=True),
        'image/object/bbox/xmin': tf.io.FixedLenSequenceFeature([], tf.float32, allow_missing=True),
    }
    # Parse the input tf.Example proto using the dictionary above.
    return tf.io.parse_single_example(example_proto, image_feature_description)



def visualize_tf(tf_file, n_instances, nrow=5, ncol=5, figsize=(30, 8)):
    """
    Plots a figure with a sample of instances in the current interactive session
   
    Parameters
    ----------
    tf_file : TYPE string
        path to tfrecord dataset from which a sample of instances are extracted.
    n : TYPE integer
        DESCRIPTION number of instances to plot.
    nrow : TYPE integer, optional
        DESCRIPTION Number of rows of the subplot grid. The default is 5.
    ncol : TYPE, optional
        DESCRIPTION Number of columns of the subplot grid. The default is 5.
    figsize : TYPE, optional
        DESCRIPTION width and height, in inches, of the main figure. The default is (30, 8).

    Returns
    -------
    Plots the instances samples in interactive session

    """
    
    
    dataset = tf.data.TFRecordDataset(tf_file)    
    parsed_dataset = dataset.map(parse_image)
    
    parsed_dataset = parsed_dataset.shuffle(50)
    
    # Create figure and axes
    fig, ax = plt.subplots(nrow, ncol, figsize=figsize,sharex='col', sharey='row', 
                           gridspec_kw={'hspace': 0, 'wspace': 0})
    
    if ncol > 1:
        plotPos_iter = [(x,y) for x in range(nrow) for y in range(ncol)]
    else: 
        plotPos_iter = [x for x in range(nrow)]
        
    i = 0

    for x in parsed_dataset.take(n_instances):
        
        img = tf.image.decode_jpeg(x['image/encoded'], channels=3).numpy()
        
        img_height = x['image/height'].numpy()
        img_width = x['image/width'].numpy()
        
        bboxes = np.array([
            x['image/object/bbox/xmin'] * img_width,
            x['image/object/bbox/ymin'] * img_height,
            x['image/object/bbox/xmax'] * img_width,
            x['image/object/bbox/ymax'] * img_height
            ])
        
        # Transpose to get bboxes coords per row
        bboxes = np.transpose(bboxes)

        #breakpoint()

        ax[plotPos_iter[i]].imshow(img)
                
        
        # Add bounding boxes to image
        for bbox in bboxes:
            
            rect = patches.Rectangle((bbox[0], bbox[1]), bbox[2] - bbox[0],
                                     bbox[3] - bbox[1], 
                                     linewidth=2, edgecolor='limegreen',
                                     facecolor='none')
            # Add the patch to the Axes
            ax[plotPos_iter[i]].add_patch(rect)
            
        i += 1
        
    plt.show()

        
