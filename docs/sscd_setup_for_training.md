# SSCD Training - Setting up

The Salmon Scale Circuli Detector (SSCD) consists of two separate object detection models: the focus detector and the circulus detector. Each detector is a YOLOv3 (*You Only Look Once*), a Convolutional Neural Network (CNN), trained for its specific purpose.

Evidence of deterioration in SSCD's performance on new images will warrant the need for retraining one of the detectors (or both). [This protocol][9] provides a guide on how to train each detector, based on the steps taken during the development of the SSCD tool.

Additional software requirements for training purposes depend on whether GPU acceleration is available, which would be the desirable hardware setting.

> For CPU-only processing, running steps 1 and 2 of [above][1] should provide all the setup required (and no need to do it twice!).
>
> To run the training protocol, launch jupyter Lab in the `sscd` conda environment and open the file `SSCD/docs/SSCD Training Protocol.ipynb`

Next we describe how to set-up a dedicated Tensorflow-GPU workstation.


## Setting up Tensorflow with GPU support

> **Author's Note**:
>
> *On setting up Tensorflow-GPU for the first time, I went through the process of installing all drivers and libraries required for configuring the use of GPU resources for parallel computing tasks, as described [here][4]. It was a longish and tricky procedure as components' versions (python, Microsoft Visual Studio, NVIDIA card and drivers, Cuda toolkit, cuDNN) must be compatible to avoid library conflicts. [Here][5], [here][6] and [here][7] are some of the online tutorials used for additional support (for Windows OS).*
>
> *Upon reviewing installation guides, I found some articles <sup>[1][2],  [2][8], [3][3]</sup> claiming that installing Tensorflow-GPU via Conda will automatically install all the required GPU processing libraries with the correct supporting versions. Unfortunately there is no easy way to test this as it would require removing the current GPU configuration and re-install everything from scratch - something I would prefer to avoid until strictly necessary. It sounds a bit too good to be true... I suspect at least some elements might need to be in place beforehand (e.g. [NVIDEA drivers][10], Microsoft Visual Studio).*
>
> *Nevertheless, I think it is worth trying the automatic Conda Tensorflow-GPU installation first before taking the longer route - simply by running `condaenv_sscd-gpu.yml` as described next.*

For reference, the YOLOv3 implementation expects **Tensoflow-GPU v2.1.0**. Assuming GPU processing has been set up correctly (as per Tendorflow's instructions), or if trying to install all requirements automatically via Conda, follow the next steps for setting up the Tensorflow-GPU workstation:

  1. Open a conda prompt (**Start** > **Anaconda** > **Anaconda Prompt**)

  2. Navigate to the SSCD directory

  3. Create the SSCD-GPU environment:

      ```
      > conda env create -f condaenv_sscd-gpu.yml
      ```

  4. Activate the environment:

    ```
    > conda activate sscd-gpu
    ```

  5. Add SSCD conda environment to Jupyter notebook

    ```
    > python -m ipykernel install --user --name sscd-gpu --display-name "SSCD-GPU"
    ```

To run the training protocol, launch a Jupyter Lab session

  ```
  > jupyter lab
  ```

and, ensuring the `SSCD-GPU` kernel is activated, open the file `SSCD/docs/SSCD Training Protocol.ipynb`.

--------
**Tip** : The Table of Contents [extension](https://github.com/jupyterlab/jupyterlab-toc) for Jupyter Lab is very useful to help navigation over long notebooks, such as the SSCD's training protocol.


[1]: ../README.md
[2]: https://towardsdatascience.com/setting-up-tensorflow-gpu-with-cuda-and-anaconda-onwindows-2ee9c39b5c44
[3]: https://towardsdatascience.com/tensorflow-gpu-installation-made-easy-use-conda-instead-of-pip-52e5249374bc
[4]: https://www.tensorflow.org/install/gpu
[5]: https://shawnhymel.com/1961/how-to-install-tensorflow-with-gpu-support-on-windows/
[6]: https://towardsdatascience.com/installing-tensorflow-with-cuda-cudnn-and-gpu-support-on-windows-10-60693e46e781
[7]: https://blog.quantinsti.com/install-tensorflow-gpu/
[8]: https://www.pugetsystems.com/labs/hpc/How-to-Install-TensorFlow-with-GPU-Support-on-Windows-10-Without-Installing-CUDA-UPDATED-1419/
<!-- [9]: ./SSCD&#32Training&#32Protocol.ipynb -->
[9]: ./SSCD%20Training%20Protocol.ipynb
[10]: https://www.nvidia.com/Download/index.aspx
