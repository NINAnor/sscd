"""
sscd-fetch: CLI tool to download SSCD data assets.

Usage:
    uv run sscd-fetch weights          # trained YOLO checkpoints (~790 MB)
    uv run sscd-fetch training-data    # training example data (~1.3 GB)
    uv run sscd-fetch darknet-weights  # pre-trained Darknet-53 weights (~248 MB)
    uv run sscd-fetch all              # all of the above
"""

import argparse
import os
import sys
import zipfile
from pathlib import Path

from sscd_libs.helpers import download_url

# ---------------------------------------------------------------------------
# Asset definitions
# ---------------------------------------------------------------------------

# Trained YOLO checkpoints for both detectors.
# URL must be a direct download link (Dropbox: use ?dl=1, not ?dl=0).
WEIGHTS_URL = (
    "https://www.dropbox.com/sh/xm2zmoz7h9g5nqi/AACfwx7_JQmUkcNK8ePXetkta?dl=1"
)
WEIGHTS_ZIP = Path("data/yoloV3_checkpoints.zip")
WEIGHTS_DIR = Path("data/yoloV3_checkpoints")
# Sentinel files that confirm a successful extraction
WEIGHTS_SENTINELS = [
    WEIGHTS_DIR / "focus_detector" / "yolov3_train_190.tf.index",
    WEIGHTS_DIR / "circuli_detector" / "yolov3_train_22.tf.index",
]

# Training example data (scale images + annotations).
# URL must be a direct download link (Dropbox: use ?dl=1).
TRAINING_DATA_URL = (
    "https://www.dropbox.com/s/fpj1svas8xgz02d/sscd_training_example_data.zip?dl=1"
)
TRAINING_DATA_ZIP = Path("data/training_example_data.zip")
TRAINING_DATA_DIR = Path("data/training_example_data")

# Pre-trained Darknet-53 weights from the original YOLOv3 authors.
# Used as the starting point for transfer learning.
DARKNET_WEIGHTS_URL = "https://pjreddie.com/media/files/yolov3.weights"
DARKNET_WEIGHTS_DIR = Path("data/transfer_learning")
DARKNET_WEIGHTS_FILE = DARKNET_WEIGHTS_DIR / "yolov3.weights"


# ---------------------------------------------------------------------------
# Individual fetch functions
# ---------------------------------------------------------------------------


def fetch_weights():
    """Download and extract the trained YOLO checkpoints."""
    if all(s.exists() for s in WEIGHTS_SENTINELS):
        print("Trained YOLO weights already present — skipping download.")
        return

    print("Downloading trained YOLO checkpoints (~790 MB)...")
    WEIGHTS_ZIP.parent.mkdir(parents=True, exist_ok=True)
    download_url(WEIGHTS_URL, str(WEIGHTS_ZIP))

    print("Extracting...")
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(WEIGHTS_ZIP, "r") as zf:
        zf.extractall(WEIGHTS_DIR)
    WEIGHTS_ZIP.unlink()

    missing = [str(s) for s in WEIGHTS_SENTINELS if not s.exists()]
    if missing:
        print(
            "WARNING: extraction completed but the following expected files are "
            f"missing:\n  " + "\n  ".join(missing),
            file=sys.stderr,
        )
    else:
        print("Trained YOLO weights ready.")


def fetch_training_data():
    """Download and extract the training example dataset."""
    if TRAINING_DATA_DIR.exists():
        print("Training example data already present — skipping download.")
        return

    print("Downloading training example data (~1.3 GB)...")
    TRAINING_DATA_ZIP.parent.mkdir(parents=True, exist_ok=True)
    download_url(TRAINING_DATA_URL, str(TRAINING_DATA_ZIP))

    print("Extracting...")
    with zipfile.ZipFile(TRAINING_DATA_ZIP, "r") as zf:
        zf.extractall(TRAINING_DATA_DIR.parent)
    TRAINING_DATA_ZIP.unlink()

    print("Training example data ready.")


def fetch_darknet_weights():
    """Download the pre-trained Darknet-53 weights for transfer learning."""
    if DARKNET_WEIGHTS_FILE.exists():
        print("Darknet weights already present — skipping download.")
        return

    print("Downloading pre-trained Darknet-53 weights (~248 MB)...")
    DARKNET_WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    download_url(DARKNET_WEIGHTS_URL, str(DARKNET_WEIGHTS_FILE))

    print("Darknet weights ready.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        prog="sscd-fetch",
        description="Download SSCD data assets (model weights, training data).",
    )
    parser.add_argument(
        "asset",
        choices=["weights", "training-data", "darknet-weights", "all"],
        help=(
            "Which asset to download: "
            "'weights' (trained YOLO checkpoints, ~790 MB), "
            "'training-data' (example training dataset, ~1.3 GB), "
            "'darknet-weights' (pre-trained Darknet-53 weights, ~248 MB), "
            "or 'all' to fetch everything."
        ),
    )
    args = parser.parse_args()

    dispatch = {
        "weights": fetch_weights,
        "training-data": fetch_training_data,
        "darknet-weights": fetch_darknet_weights,
        "all": lambda: (
            fetch_weights(),
            fetch_training_data(),
            fetch_darknet_weights(),
        ),
    }
    dispatch[args.asset]()


if __name__ == "__main__":
    main()
