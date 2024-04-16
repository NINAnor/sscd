#' Wrapper function to run python command-line function "eval_detector.py", 
#' which is part of the SSCD toolkit
eval_detections <- function(sscd_path, img_dir, anns_dir, dets_csv, iou_threshould, 
                            output_dir, plot_dets_vs_anns, sep_plots) {
  
  # list with absolute paths
  abs_paths <- list(
    eval_fun_path = file.path(sscd_path, "eval_detector.py"),
    img_dir = fs::path_abs(img_dir),
    anns_dir = fs::path_abs(anns_dir),
    dets_csv = fs::path_abs(dets_csv),
    output_dir = fs::path_abs(output_dir)
  )
  
  # Format paths for use in windows command prompt
  abs_paths_norm <- lapply(
    abs_paths, 
    function(x){
      double_quote(
        normalizePath(x)
      )
    }
  )
  
  # Build the command to run evaluation module (written in python)
  eval_py_call <- glue::glue(
    'python {abs_paths_norm$eval_fun_path}',
    '--img_dir {abs_paths_norm$img_dir}', 
    '--anns_dir {abs_paths_norm$anns_dir}',
    '--dets_csv {abs_paths_norm$dets_csv}',
    '--iou_threshould 0.5',
    '--output_dir {abs_paths_norm$output_dir}',
    '--plot_dets_vs_anns {ifelse(plot_dets_vs_anns, "True", "False")}',
    '--sep_plots {ifelse(sep_plots, "True", "False")}',
    .sep = " "
  )
  
  # Invoke system command
  system(eval_py_call, invisible = FALSE)
  
}

