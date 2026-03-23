# SSCD Training - Setting up

The Salmon Scale Circuli Detector (SSCD) consists of two separate object detection models: the focus detector and the circulus detector. Each detector is a YOLOv3 (*You Only Look Once*), a Convolutional Neural Network (CNN), trained for its specific purpose.

Evidence of deterioration in SSCD's performance on new images will warrant the need for retraining one of the detectors (or both). [This protocol][9] provides a guide on how to train each detector, based on the steps taken during the development of the SSCD tool.

Additional software requirements for training purposes depend on whether GPU acceleration is available, which would be the desirable hardware setting.

> For CPU-only processing, simply follow the standard installation below. No need for additional steps!
>
> To run the training protocol, launch Jupyter Lab in the `sscd` environment and open the file `SSCD/docs/SSCD Training Protocol.ipynb`

Next we describe how to set-up a dedicated Tensorflow-GPU workstation.


## Setting up Tensorflow with GPU support

> **Note**:
>
> *On setting up Tensorflow-GPU for the first time, configuring GPU drivers and libraries (CUDA, cuDNN) can be complex as component versions must be compatible. Refer to [TensorFlow's GPU installation guide][4] for detailed instructions.*
>
> *Using UV, GPU setup is straightforward: install the standard environment and configure the GPU drivers and libraries as described below.*

TensorFlow 2.16 and later includes GPU support in the main `tensorflow` package — there is no separate `tensorflow-gpu` package. Follow these steps to set up the GPU-enabled environment:

1. **Clone and install dependencies**

   ```bash
   git clone <repository-url>
   cd sscd
   uv sync --dev
   ```

2. **Register the Jupyter kernel (optional, for separate GPU kernel)**

   ```bash
   uv run ipython kernel install --user --env VIRTUAL_ENV $(pwd)/.venv --name=sscd-gpu
   ```

3. **Launch Jupyter Lab**

   ```bash
   uv run --with jupyter jupyter lab
   ```

Open the training protocol notebook `SSCD/docs/SSCD Training Protocol.ipynb` and ensure the `sscd-gpu` kernel (or the default `sscd` if you reused it) is selected.

--------
**Tip**: The Table of Contents [extension](https://github.com/jupyterlab/jupyterlab-toc) for Jupyter Lab is very useful to help navigation over long notebooks, such as the SSCD's training protocol.


[1]: ../README.md
[4]: https://www.tensorflow.org/install/gpu
[9]: ./SSCD%20Training%20Protocol.ipynb
