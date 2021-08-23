'''Splits image filenames (ID's) to use in training, validation and testing sets

Notes: 
    (i) ID's are shuffled before splitting
    (ii) images without corresponding annotation files are dropped

Example usage:
    python create_splits.py \
    --images_dir "./data/scales_data_sample/images/"\
    --annotations_dir "./data/scales_data_sample/annotations/"\
    --output_dir "./data/scales_data_sample/image_sets/"\
    --output_prefix "scales"\
    --split  "0.6:0.2:0.2"\    

Outputs txt files with filenames of images to be used in training, validation and testing (one txt file per set)

'''

from pathlib import Path
import os
import math
import pandas as pd
import argparse


# ------------------------------------------------------------------------------
# -- Parse the command line arguments

args_parser = argparse.ArgumentParser(
    description = "Splits image filenames (ID's) to use for training, validation and test sets",
    formatter_class=argparse.MetavarTypeHelpFormatter
    )
args_parser.add_argument(
    "--images_dir",
    required=True,
    type=str,
    help="path to directory containing image files",
)
args_parser.add_argument(
    "--annotations_dir",
    required=True,
    type=str,
    help="path to directory containing annotation files"
)
args_parser.add_argument(
    "--output_dir",
    required=True,
    type=str,
    help="path to directory where split files are stored"
)

args_parser.add_argument(
    "--output_prefix",
    required=False,
    type=str,
    default = '',
    help="prefix to be used in output split files"
)

args_parser.add_argument(
        "--split",
        required=False,
        type=str,
        default="0.6:0.2:0.2",
        help="colon-separated triple of ratios to use for training, "
             "validation, and testing (values should sum to 1.0). "
            "Default is '0.6:0.2:0.2'"
)

args = vars(args_parser.parse_args())  # 'vars' converts Namespace containing args to dict


# ------------------------------------------------------------------------------
def get_ids_table(directory):
    
    """ Get filenames from target directory
    Args:
        directory: string, specifying the path to the folder containing the files 
            whose names (ID's) are to be extracted
        
    Returns:
        a panda dataframe with shaped ("n", 2) with ID's and filenames contained in
            target folder, where "n" is the number of files in the folder
    """
    
    # get filenames
    filenames = os.listdir(directory)
    # get basenames
    basenames = [Path(f).stem for f in filenames]
    # generate dict with 
    ids_d = { 
    "id" : basenames,
    "filename" : filenames
    }
    
    ids_df = pd.DataFrame(ids_d)
    return(ids_df)



# ------------------------------------------------------------------------------
def split_train_valid_test_filenames( img_files, ann_files):
    """ Core module function - Self-explanatory...
    
    Args:
        img_fnames: panda dataframe, containing the IDs and the corresponding filenames of 
            images to split
        ann_fnames: panda dataframe, containing the IDs and the corresponding filenames of 
            annotations to split
            
    Return:
        three pandas datasets with the filenames and ids of images in each training, 
            validation and testing split.
    """
   
    # find matching images-annotations IDs
    ids_to_split = list(set(img_files.id).intersection(ann_files.id))
    
    # find unmatched image/annotations
    ids_noAnnotation = list(set(img_files.id).difference(ann_files.id))
    num_ids_noAnnotation = len(ids_noAnnotation)

    if num_ids_noAnnotation > 0:
        print("Following ID(s) discarded due to missing image-annotation ID match:")
        print("-----------------------------------")
        print(*ids_noAnnotation, sep = "\n")
        print("-----------------------------------\n")
        
    if len(ids_to_split) == 0:
        raise ValueError("No annotations available for any of the images")

    # get images to split into training, validation and test sets
    img_files_labelled = img_files.loc[img_files.id.isin(ids_to_split)]
    
    # Extract splits percentages from the argument
    train_pctge, valid_pctge, test_pctge = [float(x) for x in args['split'].split(":")]

    # confirm that percentages add up to 100%
    total_pctge = train_pctge + valid_pctge + test_pctge
    if not math.isclose(1.0, total_pctge):
        raise ValueError("Invalid argument values: the combined train/valid/test "
                         "percentages do not add to 1.0"
                        )

    # split the file IDs into training and validation lists
    # get the split based on the number of labelled images and split percentages
    # images are shuffled before splits are applied
    img_files_labelled = img_files_labelled.sample(frac=1)  # shuffle dataset

    final_train_index = int(round(train_pctge * len(img_files_labelled)))
    final_valid_index = int(round((train_pctge + valid_pctge) * len(img_files_labelled)))

    train_files = img_files_labelled.iloc[:final_train_index]
    valid_files = img_files_labelled.iloc[final_train_index:final_valid_index]
    trainval_files = img_files_labelled.iloc[:final_valid_index]
    test_files = img_files_labelled.iloc[final_valid_index:]

    split_summary = {
        "Training set:": len(train_files),
        "Validation set:": len(valid_files),
        "Testing set:": len(test_files)
    }

    if sum(split_summary.values()) == len(ids_to_split):
        print("A total of", len(ids_to_split), "image IDs were split into the following sets:")
        print("----------------------------------")
        for key in split_summary:
            print(key, split_summary[key], "image IDs")
        print("----------------------------------")
    else:
        print("Warning: splits sizes do not sum up to total labelled images")
        
    return train_files, valid_files, trainval_files, test_files



# ------------------------------------------------------------------------------
def write_split(img_filename, out_dir, out_prefix, splitname):
    dest_path = os.path.join(out_dir, "%s%s.txt" % (out_prefix, splitname))
    img_filename.to_csv(dest_path, header=False, index = False)


    
# ------------------------------------------------------------------------------
def main():
    
    # IDs table for images
    img_files = get_ids_table(args['images_dir'])
    #img_files = img_files.rename(columns = {'filename': 'img_filename'})

    # IDs table for annotations
    ann_files = get_ids_table(args['annotations_dir'])
    #ann_files = ann_files.rename(columns = {'filename': 'ann_filename'})
    
    train_files, valid_files, trainval_files, test_files = split_train_valid_test_filenames(img_files, ann_files)
    
    os.makedirs(args['output_dir'], exist_ok=True)
    
    write_split(train_files["filename"], args['output_dir'], args['output_prefix'], "train")
    write_split(valid_files["filename"], args['output_dir'], args['output_prefix'], "valid")
    write_split(trainval_files["filename"], args['output_dir'], args['output_prefix'], "trainval")
    write_split(test_files["filename"], args['output_dir'], args['output_prefix'], "test")
    

if __name__ == '__main__':
    main()