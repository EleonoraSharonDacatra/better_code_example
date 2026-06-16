# TODO: transform into json file
from skimage.filters import threshold_otsu, threshold_yen
from . import utilities 

acceptableNumberOfChannels = 2

# TODO: Ask about threshold choice
acceptableTypes = {
    "DAPI": {"channel":0, 
        "sigmaGaussianBackground":20, 
        "sigmaGaussian":1.5, 
        "thresholdDet0":200,
        "thresholdOtsu":128},
    "GFP": {"channel":1, 
       "sigmaGaussianBackground":25, 
        "sigmaGaussian":2.0, 
        "thresholdDet0":150, # tried 100, too many false positives
        "thresholdOtsu":256}
}

acceptableDet = {
    0: utilities.detect_fixed_threshold,
    1: utilities.detect_otsu,
    2: utilities.detect_yen,
}