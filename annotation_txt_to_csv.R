# Convert annotation txt files to a single detections csv for use in ealuation
#
# To convert xml to txt run Python script annotation_xml_to_txt.py first
library(tidyverse)


ann_dir <- "Z://Adult_Salmon_Scales/Salmon_scale_circuli_detection/SSCD_data/detection_accuracy_analysis/sscd_detections_90_txt/"

ann_path <- list.files(ann_dir, pattern = ".txt", full.names = TRUE)
img_ids <- tools::file_path_sans_ext(fs::path_file(ann_path))

# create folder to dump converted files
det_dir <- str_replace(ann_dir, "_txt", "_dets")
dir.create(det_dir, showWarnings = FALSE)

dets <- map2(ann_path, img_ids, .f = function(x, y){
  read.table(x, col.names = c("class_name", "confidence","xmin", "ymin", "xmax", "ymax")) %>%
    add_column(
      img_id = y, 
      detection_nr = 1:nrow(.),
      .before = "class_name") %>%
    add_column(score = 1, .after = "class_name") %>%
    add_column(img_prop = NA)
}) %>%
  bind_rows() 

write_csv(dets, file.path(det_dir, "detections.csv"))







## 3-way comparison in terms of Average Precision


# # SSCD Vs Bruno
# eval_detections(
#   sscd_path,
#   img_dir = "../data/transect_imgs/",
#   anns_dir = "../data/circulus_anns_Bruno_xml/",
#   dets_csv = "../data/sscd_detections/detections.csv", 
#   output_dir = "../data/sscd_vs_Bruno", 
#   iou_threshould = 0.5,
#   plot_dets_vs_anns = TRUE, 
#   sep_plots = TRUE)





# SSCD Vs Jason
# eval_detections(
#   sscd_path,
#   img_dir = "../data/transect_imgs/",
#   anns_dir = "../data/circulus_anns_Jason_xml/",
#   dets_csv = "../data/sscd_detections/detections.csv", 
#   output_dir = "../data/sscd_vs_Jason", 
#   iou_threshould = 0.5,
#   plot_dets_vs_anns = TRUE, 
#   sep_plots = TRUE)




# eval_detections(
#   sscd_path,
#   img_dir = "../data/transect_imgs/",
#   anns_dir = "../data/circulus_anns_Bruno_xml/",
#   dets_csv = "../data/dets_Jason/detections.csv", 
#   output_dir = "../data/Jason_vs_Bruno", 
#   iou_threshould = 0.5,
#   plot_dets_vs_anns = TRUE, 
#   sep_plots = TRUE)






# 
# <!-- ```{r} -->
#   <!-- # Bruno Vs Jason (Jason as ground truth) -->
#   <!-- eval_detections( -->
#                           <!--   sscd_path, -->
#                           <!--   img_dir = "../data/transect_imgs/", -->
#                           <!--   anns_dir = "../data/circulus_anns_Jason_xml/", -->
#                           <!--   dets_csv = "../data/dets_Bruno/detections.csv",  -->
#                           <!--   output_dir = "../data/Bruno_vs_Jason",  -->
#                           <!--   iou_threshould = 0.5, -->
#                           <!--   plot_dets_vs_anns = TRUE,  -->
#                           <!--   sep_plots = TRUE) -->
#   <!-- ``` -->

