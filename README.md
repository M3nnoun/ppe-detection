# PPE Detection

Detecting personal protective equipment on construction sites with a fine-tuned YOLOv8 model,
served through a small Flask web app.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![YOLOv8](https://img.shields.io/badge/YOLOv8-ultralytics-00FFFF)
![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch&logoColor=white)

## Problem

Site safety audits are manual: someone watches footage or walks the site checking that workers are
wearing hard hats, vests, gloves and goggles. This project automates the visual check — given an
image, flag both the PPE that is present and, critically, the PPE that is *missing*.

The class design reflects that goal. The model does not just detect a hard hat; it has separate
classes for `Hardhat` and `NO-Hardhat`, so a violation is a positive detection rather than the
absence of one. That makes downstream alerting straightforward.

## Model

A **YOLOv8n** checkpoint fine-tuned on a 14-class PPE dataset.

| Setting | Value |
|---------|-------|
| Base model | `yolov8n.pt` |
| Epochs | 50 |
| Image size | 640 |
| Batch size | 16 |
| Optimizer | `auto` |
| Augmentation | mosaic, HSV jitter, horizontal flip, random erasing |
| Trained on | Google Colab (single GPU) |

Full training configuration is preserved in [`models/args.yaml`](models/args.yaml).

### Classes

`Hardhat` · `NO-Hardhat` · `Safety Vest` · `NO-Safety Vest` · `Gloves` · `NO-Gloves` ·
`Goggles` · `NO-Goggles` · `Mask` · `NO-Mask` · `Person` · `Ladder` · `Safety Cone` ·
`Fall-Detected`

The class distribution is **heavily imbalanced** — `Hardhat` accounts for roughly 29,000 instances
while `Ladder` has around 700. Expect the rarer classes (`Ladder`, `Person`, `NO-Mask`) to perform
substantially worse than the head classes, and treat any single overall mAP figure with suspicion.
See [`models/labels.jpg`](models/labels.jpg) for the full distribution and bounding-box statistics,
and `models/train_batch*.jpg` for augmented training samples.

## Application

A Flask app wrapping the detector:

- `GET /` renders an upload form.
- `POST /` saves the uploaded image, runs detection at `conf=0.25`, writes the annotated output to
  `static/uploads/result.jpg`, and renders it.

Inference runs on CUDA when available and falls back to CPU automatically
([`src/config.py`](src/config.py)).

## Repository structure

```
main.py              Flask app factory and entry point
app/
  routes.py          Upload and detection route
  services.py        Placeholder — currently empty
src/
  config.py          Model path, device selection, thresholds
  detector.py        YOLO model loading and inference wrapper
  video.py           Webcam MJPEG frame generator (implemented, not yet routed)
models/
  args.yaml          Training hyperparameters
  labels.jpg         Class distribution and box statistics
  train_batch*.jpg   Augmented training batch samples
templates/           Upload and result pages
requirements.txt
```

## Setup

> **The trained weights are not in this repository.** `src/config.py` expects `models/best.pt`
> (excluded for size). Supply your own fine-tuned checkpoint at that path, or point `MODEL_PATH` at
> a stock model such as `yolov8n.pt` to smoke-test the plumbing. The app will not start without it.

```bash
git clone https://github.com/M3nnoun/ppe-detection.git
cd ppe-detection
pip install -r requirements.txt

# place your trained checkpoint here
# models/best.pt

# the upload directory is not tracked and must exist before the first request
mkdir -p static/uploads

python main.py
```

Then open <http://127.0.0.1:5000>.

## Current limitations

- **Weights are not distributed with the repo**, so it is not runnable as cloned (see above).
- **Webcam streaming is unfinished.** `src/video.py` implements a working MJPEG generator, but no
  route exposes it — the app is image-upload only. Wiring it up needs a `/video_feed` route
  returning `Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')`.
- **`app/services.py` is an empty placeholder**, left from the intended split between routing and
  business logic. The detection call currently sits directly in the route.
- **Uploads are saved under their original filename** with no sanitisation or collision handling, and
  results always overwrite the same `result.jpg`. Fine for a local demo, not for concurrent use.
- **No evaluation metrics are published here.** Validation ran during training but the results were
  not exported into the repository, so the model's actual mAP is undocumented.
