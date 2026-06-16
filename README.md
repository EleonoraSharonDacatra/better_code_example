# Spot detection in fluorescence images
This python package detects fluorescent spots in a 2-channel microscopy image and compute the overlap (co-localization).

Channel 1: DAPI (nuclear stain)
Channel 2: GFP (protein of interest)

Det 0: fixed threshold
Det 1: Otsu
Det 2: Yen

parameters.py file describes acceptable types and Det

## Local installation

```bash
pip install -e .
```

## Quick Start

```python
from spot_detection import SpotDetection

# Initialize the detector with an image path, channel types, and detection method
detector = SpotDetection(
    path="path/to/image.tif",
    types=["DAPI", "GFP"], 
    det=1  
)

# Run the analysis
detector.run()

# The two masks are saved automatically as .tif files and statistics are computed and saved in the same folder as the original image
```
