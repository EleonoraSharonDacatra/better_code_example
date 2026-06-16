from skimage.filters import gaussian
from skimage.measure import label

import logging
import os

import numpy as np
from . import utilities, parameters, logger

class SpotDetection:
    # Spot detection class: does not depend on the specific methods
    def __init__(self, path, types, det):
        self.logger = logger.setup_logger("logger", level=logging.INFO)
        self.path = path
        self.basePath = os.path.dirname(self.path) + os.sep
        self.types = types
        self.det = det
        self.results = {}

    def run(self):
        self.readImage()
        self.computeSpotsForEachType()
        self.computeStatistics()
        self.BuildRGBComposite()
        self.saveResults()

    def readImage(self):
        if self.path.endswith(".tif"):
            self.img = utilities.readTiffImage(self.path, self.logger)
            shape = self.img.shape
            #TODO: Extend to support more channels 
            if shape[0] != parameters.acceptableNumberOfChannels:
                self.logger.error(f"Image has {shape[0]} channels, but expected {parameters.acceptableNumberOfChannels}.")
                raise ValueError("Unexpected number of channels in image.")
        else:
            self.logger.error(f"Image is not a .tif image")
            raise ValueError("Only .tif images supported")

    def computeSpotsForEachType(self):
        for type in self.types:
            if type in parameters.acceptableTypes:
                self.par = parameters.acceptableTypes[type]
            else:
                self.logger.error(f"Type not configured.")
                raise ValueError("Type not configured")
            ch, ch_smooth, ch_spots, n_spots_ch = self.detectSpots(type)
            self.results[type] = {
                "ch": ch,
                "ch_smooth": ch_smooth,
                "ch_spots": ch_spots,
                "n_spots_ch": n_spots_ch,
            }
            self.plot_graph(ch, ch_smooth, ch_spots, type)

    def detectSpots(self, type):
    
        ch = self.img[self.par['channel']]

        # Subtract background
        background = gaussian(ch, sigma=self.par['sigmaGaussianBackground'])
        ch_no_bg = ch - background
        ch_no_bg[ch_no_bg < 0] = 0
        ch_smooth = gaussian(ch_no_bg, sigma=self.par['sigmaGaussian'])

        # Detect spots
        if self.det in parameters.acceptableDet:
            detection_func = parameters.acceptableDet[self.det]

            if self.det == 0:
                ch_spots = detection_func(ch_smooth, self.par['thresholdDet0'])
            elif self.det == 1:
                ch_spots = detection_func(ch_smooth, self.par['thresholdOtsu'])
            elif self.det == 2:
                ch_spots = detection_func(ch_smooth)
        else:
            self.logger.error(f"Det not configured.")
            raise ValueError("Det not configured")

        ch0_labeled = label(ch_spots)
        n_spots_ch = ch0_labeled.max()
        self.logger.info("%s spots: %d", type, n_spots_ch)
        return ch, ch_smooth, ch_spots, n_spots_ch
    
    def plot_graph(self, ch, ch_smooth, ch_spots, type):
        titles = [type + " raw", type + " smoothed", type + " spots"]
        colors = ["gray", "gray", "gray"]
        utilities.plotGraph(ch, ch_smooth, ch_spots, titles, colors)

    def computeStatistics(self):
        spots = []
        self.stats = {}
        for type in self.types:
            results = self.results.get(type)
            ch = results["ch"]
            mean = np.mean(ch)
            std = np.std(ch)
            min_val = int(np.min(ch))
            max_val = int(np.max(ch))
            self.logger.info(f"{type:5s} -- mean: {mean:.1f}  std: {std:.1f}  min: {min_val}  max: {max_val}")
            spots.append(self.results[type]["ch_spots"])
            self.stats[type] = {
                "mean": mean,
                "std": std,
                "min": min_val,
                "max": max_val,
            }
            
        overlap_mask = np.logical_and.reduce(spots)
        union_mask = np.logical_or.reduce(spots)
        n_overlap = int(np.sum(overlap_mask))
        overlap_pct = 100.0 * n_overlap / int(np.sum(union_mask)) if np.sum(union_mask) else 0.0
        self.logger.info("Overlap pixels: %d  (%.1f%% of union)" % (n_overlap, overlap_pct))
        self.stats["overlap"] = {
            "n_overlap": n_overlap,
            "overlap_pct": overlap_pct,
        }

    def BuildRGBComposite(self):
        # TODO: (enhancement) would it be useful to extend this to more than 2 types?
        ch0_spots = self.results[self.types[0]]["ch_spots"]
        ch1_spots = self.results[self.types[1]]["ch_spots"]
        rgb = np.zeros((self.img.shape[1], self.img.shape[2], 3), dtype=np.uint8)
        rgb[ch0_spots, 0] = 255  # red channel  -> DAPI spots
        rgb[ch1_spots, 1] = 255  # green channel -> GFP spots
        # where both masks are true the pixel becomes yellow (red+green)

        titles = [f"{self.types[0]} mask", f"{self.types[1]} mask", f"Overlay (red={self.types[0]}, green={self.types[1]}, yellow=overlap)"]
        colors = ["Reds", "Greens"]
        utilities.plotGraph(ch0_spots, ch1_spots, rgb, titles, colors)

        for type, results in self.results.items():
            fileName = self.basePath + f"{type.lower()}_mask.tif"
            utilities.writeTifImage(fileName, results["ch_spots"].astype(np.uint8))

    def saveResults(self):

        n_spots_ch0 = int(self.results[self.types[0]].get("n_spots_ch", 0))
        n_ch1_spots = int(self.results[self.types[1]].get("n_spots_ch", 0))
        with open(self.basePath + "results.txt", "w") as f:
            f.write("=== Spot counts ===\n")
            f.write(f"{self.types[0]}: " + str(int(n_spots_ch0)) + "\n")
            f.write(f"{self.types[1]}: " + str(int(n_ch1_spots)) + "\n")
            f.write("\n")
            f.write("=== Channel statistics ===\n")
            f.write(f"{self.types[0]} mean: " + str(round(self.stats[self.types[0]]["mean"], 2)) + "\n")
            f.write(f"{self.types[0]} std: " + str(round(self.stats[self.types[0]]["std"], 2)) + "\n")
            f.write(f"{self.types[0]} min: " + str(self.stats[self.types[0]]["min"]) + "\n")
            f.write(f"{self.types[0]} max: " + str(self.stats[self.types[0]]["max"]) + "\n")
            f.write(f"{self.types[1]} mean: " + str(round(self.stats[self.types[1]]["mean"], 2)) + "\n")
            f.write(f"{self.types[1]} std: " + str(round(self.stats[self.types[1]]["std"], 2)) + "\n")
            f.write(f"{self.types[1]} min: " + str(self.stats[self.types[1]]["min"]) + "\n")
            f.write(f"{self.types[1]} max: " + str(self.stats[self.types[1]]["max"]) + "\n")
            f.write("\n")
            f.write("=== Mask overlap ===\n")
            f.write("Overlap pixels: " + str(self.stats["overlap"]["n_overlap"]) + "\n")
            f.write("Overlap percentage: " + str(round(self.stats["overlap"]["overlap_pct"], 1)) + "%\n")
