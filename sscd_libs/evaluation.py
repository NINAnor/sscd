# -*- coding: utf-8 -*-
"""
Created on Wed Mar 1 09:34:24 2021

@author: Bruno Caneco

Module containing the core code to perform object detection evaluation. Mostly
based on tool published in https://github.com/rafaelpadilla/Object-Detection-Metrics.

'This project applies the most popular metrics used to evaluate object detection '
'algorithms.\nThe current implemention runs the Pascal VOC metrics.\nFor further references, '
'please check:\nhttps://github.com/rafaelpadilla/Object-Detection-Metrics',
"Developed by: Rafael Padilla (rafael.padilla@smt.ufrj.br)"

Changes to original code include the addition of the F1 metric & mean centre error
Also, some corrections required to finish the run in the original working directory

"""



import glob
import os
import sys
from pathlib import Path
import logging

# import local packages
from obj_det_metrics.lib.utils import (
    BBType,
    BBFormat,
    CoordinatesType
    )

from obj_det_metrics.lib.BoundingBoxes import BoundingBoxes
from obj_det_metrics.lib.BoundingBox import BoundingBox
from obj_det_metrics.lib.Evaluator import *

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Validate formats
def ValidateFormats(argFormat, argName, errors):
    if argFormat == 'xywh':
        return BBFormat.XYWH
    elif argFormat == 'xyrb':
        return BBFormat.XYX2Y2
    elif argFormat is None:
        return BBFormat.XYWH  # default when nothing is passed
    else:
        errors.append(
            'argument %s: invalid value. It must be either \'xywh\' or \'xyrb\'' % argName)

# ------------------------------------------------------------------------------
# Validate mandatory args
def ValidateMandatoryArgs(arg, argName, errors):
    if arg is None:
        errors.append('argument %s: required argument' % argName)
    else:
        return True

# ------------------------------------------------------------------------------
def ValidateImageSize(arg, argName, argInformed, errors):
    errorMsg = 'argument %s: required argument if %s is relative' % (argName, argInformed)
    ret = None
    if arg is None:
        errors.append(errorMsg)
    else:
        arg = arg.replace('(', '').replace(')', '')
        args = arg.split(',')
        if len(args) != 2:
            errors.append(
                '%s. It must be in the format \'width,height\' (e.g. \'600,400\')' % errorMsg)
        else:
            if not args[0].isdigit() or not args[1].isdigit():
                errors.append(
                    '%s. It must be in INTEGER the format \'width,height\' (e.g. \'600,400\')' %
                    errorMsg)
            else:
                ret = (int(args[0]), int(args[1]))
    return ret

# ------------------------------------------------------------------------------
# Validate coordinate types
def ValidateCoordinatesTypes(arg, argName, errors):
    if arg == 'abs':
        return CoordinatesType.Absolute
    elif arg == 'rel':
        return CoordinatesType.Relative
    elif arg is None:
        return CoordinatesType.Absolute  # default when nothing is passed
    errors.append('argument %s: invalid value. It must be either \'rel\' or \'abs\'' % argName)


# ------------------------------------------------------------------------------
def getBoundingBoxes(directory,
                      isGT,
                      bbFormat,
                      coordType,
                      allBoundingBoxes=None,
                      allClasses=None,
                      imgSize=(0, 0)):
    """Read txt files containing bounding boxes (ground truth and detections)."""
    if allBoundingBoxes is None:
        allBoundingBoxes = BoundingBoxes()
    if allClasses is None:
        allClasses = []
    # Read ground truths
    files = glob.glob(directory + os.path.sep + "*.txt")
    files.sort()
    # Read GT detections from txt file
    # Each line of the files in the groundtruths folder represents a ground truth bounding box
    # (bounding boxes that a detector should detect)
    # Each value of each line is  "class_id, x, y, width, height" respectively
    # Class_id represents the class of the bounding box
    # x, y represents the most top-left coordinates of the bounding box
    # x2, y2 represents the most bottom-right coordinates of the bounding box
    for f in files:
        #reakpoint()
        #nameOfImage = f.replace(".txt", "")
        nameOfImage = Path(f).stem
        fh1 = open(f, "r")
        for line in fh1:
            line = line.replace("\n", "")
            if line.replace(' ', '') == '':
                continue
            splitLine = line.split(" ")
            if isGT:
                # idClass = int(splitLine[0]) #class
                idClass = (splitLine[0])  # class
                x = float(splitLine[1])
                y = float(splitLine[2])
                w = float(splitLine[3])
                h = float(splitLine[4])
                bb = BoundingBox(
                    nameOfImage,
                    idClass,
                    x,
                    y,
                    w,
                    h,
                    coordType,
                    imgSize,
                    BBType.GroundTruth,
                    format=bbFormat)
            else:
                # idClass = int(splitLine[0]) #class
                idClass = (splitLine[0])  # class
                confidence = float(splitLine[1])
                x = float(splitLine[2])
                y = float(splitLine[3])
                w = float(splitLine[4])
                h = float(splitLine[5])
                bb = BoundingBox(
                    nameOfImage,
                    idClass,
                    x,
                    y,
                    w,
                    h,
                    coordType,
                    imgSize,
                    BBType.Detected,
                    confidence,
                    format=bbFormat)
            allBoundingBoxes.addBoundingBox(bb)
            if idClass not in allClasses:
                allClasses.append(idClass)
        fh1.close()
    return allBoundingBoxes, allClasses


# ------------------------------------------------------------------------------
def evaluate(gtFolder, detFolder, savePath, iouThreshold = 0.5, gtFormat = 'xywh', 
             detFormat = 'xywh', gtCoordinates = 'abs', detCoordinates = 'abs', 
             imgSize = (0,0), showPlot = True, get_details = False):

    """
    Main function for evaluating of object detection model performance. Basically rewriting 
    code in pascalvoc.py so that it can be ported as the sscd's evaluation tool
    
    
    Parameters
    ----------
    detFolder : str
        folder containing your ground truth bounding boxes
    detFolder : str
        folder containing your detected bounding boxes.
    savePath : str
        folder where the plots are saved.
    iouThreshold : float, optional
        IOU threshold. The default is 0.5.
    gtFormat : str, optional
        format of the coordinates of the ground truth bounding boxes: '
        '(\'xywh\': <left> <top> <width> <height>)'
        ' or (\'xyrb\': <left> <top> <right> <bottom>). The default is 'xywh'.
    detFormat : str, optional
        format of the coordinates of the detected bounding boxes '
        '\'xywh\': <left> <top> <width> <height> '
        'or \'xyrb\': <left> <top> <right> <bottom>. The default is 'xywh'.
    gtCoordinates : str, optional
        reference of the ground truth bounding box coordinates: absolute '
        'values (\'abs\') or relative to its image size (\'rel\'). The default is 'abs'.
    detCoordinates : str, optional
        reference of the ground truth bounding box coordinates: '
        'absolute values (\'abs\') or relative to its image size (\'rel\'). The default is 'abs'.
    imgSize : TYPE, optional
        image size. Required if -gtcoords or -detcoords are \'rel\'. The default is None.
    showPlot : boolean, optional
        no plot is shown during execution. The default is True.
    get_details: boolean, optional
        If True, returns detailed evaluation data on detections and ground truths 
        (e.g iou per detection, detected gts).

    Returns
    -------
    int
        DESCRIPTION.

    """
   
    # Arguments validation
    errors = []
    
    # Validate formats
    gtFormat = ValidateFormats(gtFormat, '-gtformat', errors)
    detFormat = ValidateFormats(detFormat, '-detformat', errors)
   
    # Coordinates types
    gtCoordType = ValidateCoordinatesTypes(gtCoordinates, '-gtCoordinates', errors)
    detCoordType = ValidateCoordinatesTypes(detCoordinates, '-detCoordinates', errors)
        
    if gtCoordType == CoordinatesType.Relative:  # Image size is required
        imgSize = ValidateImageSize(imgSize, '-imgsize', '-gtCoordinates', errors)
    if detCoordType == CoordinatesType.Relative:  # Image size is required
        imgSize = ValidateImageSize(imgSize, '-imgsize', '-detCoordinates', errors)
        
    # If error, show error messages
    if len(errors) != 0:
        print('Object Detection Metrics: error(s): ')
        [print(e) for e in errors]
        sys.exit()
        
    
    # Get groundtruth boxes
    allBoundingBoxes, allClasses = getBoundingBoxes(
        gtFolder, True, gtFormat, gtCoordType, imgSize=imgSize)
    
    # Get detected boxes
    allBoundingBoxes, allClasses = getBoundingBoxes(
        detFolder, False, detFormat, detCoordType, allBoundingBoxes, allClasses, imgSize=imgSize)
    allClasses.sort()
    
    evaluator = Evaluator()
    acc_AP = 0
    validClasses = 0
    
    #breakpoint()
    # Plot Precision x Recall curve
    detections, res_by_image, dets_details, gts_details = evaluator.PlotPrecisionRecallCurve(
        allBoundingBoxes,  # Object containing all bounding boxes (ground truths and detections)
        IOUThreshold=iouThreshold,  # IOU threshold
        method=MethodAveragePrecision.EveryPointInterpolation,
        showAP=True,  # Show Average Precision in the title of the plot
        showInterpolatedPrecision=False,  # Don't plot the interpolated precision curve
        savePath=savePath,
        showGraphic=showPlot, 
        get_details=get_details)
    
    loggerText = ["Evaluation results:\n\n"]
    
    f = open(os.path.join(savePath, 'evaluation_results.txt'), 'w')
    f.write('Object Detection Metrics\n')
    f.write('Average Precision (AP), Mean Center Error (MEC), Precision and Recall per class:')
    
    # each detection is a class
    for metricsPerClass in detections:
    
        #breakpoint()
        # Get metric values per each class
        cl = metricsPerClass['class']
        ap = metricsPerClass['AP']
        precision = metricsPerClass['precision']
        recall = metricsPerClass['recall']
        totalPositives = metricsPerClass['total positives']
        total_TP = int(metricsPerClass['total TP'])
        total_FP = int(metricsPerClass['total FP'])
        total_FN = int(totalPositives - total_TP)
        MCE = round(metricsPerClass['mean center error'], 4)
        F1 = round(total_TP/(total_TP + (total_FN + total_FP)/2), 4)
        
        if totalPositives > 0:
            validClasses = validClasses + 1
            acc_AP = acc_AP + ap
            prec = ['%.2f' % p for p in precision]
            rec = ['%.2f' % r for r in recall]
            ap_str = "{0:.2f}%".format(ap * 100)
            
            # ap_str = "{0:.4f}%".format(ap * 100)
            # print('TP=%s; FP=%s; FN=%s (%s)' % (total_TP,total_FP, total_FN, cl))
            # print('AP: %s (%s)' % (ap_str, cl))
            # print('MCE: %s (%s)' % (MCE, cl))
            # print('F1: %s (%s)' % (F1, cl))
            f.write('\n\nClass: %s' % cl)
            f.write('\nAP: %s' % ap_str)
            f.write('\nMCE: %s' % MCE)
            f.write('\nF1: %s' % F1)
            f.write('\n\nPrecision: %s' % prec)
            f.write('\nRecall: %s' % rec)
            
            loggerText.append('\tTP = %s; FP = %s; FN = %s (%s)\n' % (total_TP,total_FP, total_FN, cl))
            loggerText.append('\tAP: %s (%s)\n' % (ap_str, cl))
            loggerText.append('\tMCE: %s (%s)\n' % (MCE, cl))
            loggerText.append('\tF1: %s (%s)\n' % (F1, cl))
    
    mAP = acc_AP / validClasses
    mAP_str = "{0:.2f}%".format(mAP * 100)
    # print('mAP: %s' % mAP_str)
    f.write('\n\n\nmAP: %s' % mAP_str)
    loggerText.append('\t......................\n\tmAP: %s\n' % mAP_str)
    
    
    #breakpoint()
    logger.info("".join(loggerText))
    
    # write-out results by image
    res_by_image.to_csv(os.path.join(savePath, 'results_by_image.csv'), index=None)
    
    if get_details:
        dets_details.to_csv(os.path.join(savePath, 'det_details.csv'), index=None)
        gts_details.to_csv(os.path.join(savePath, 'gt_details.csv'), index=None)
    
    return 0 #res_by_image